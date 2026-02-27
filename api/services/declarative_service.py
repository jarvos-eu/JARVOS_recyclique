# Service agrégats déclaratifs (Story 9.1).
# Source : sale_items (weight, category_id ; période depuis sales.sale_date ou sales.created_at),
#          ligne_depot (poids_kg, category_id ; période depuis created_at).
# Réexécutable par période (year, quarter) pour backfill / corrections.

import logging
from datetime import datetime, timezone
from typing import List, Tuple
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from api.models.declarative import DeclarativeAggregate
from api.models.ligne_depot import LigneDepot
from api.models.sale import Sale
from api.models.sale_item import SaleItem

logger = logging.getLogger(__name__)

FLOW_CAISSE = "caisse"
FLOW_RECEPTION = "reception"


def _quarter_bounds(year: int, quarter: int) -> Tuple[datetime, datetime]:
    """Retourne (début, fin) du trimestre en timezone-aware UTC (fin = premier jour du trimestre suivant)."""
    if quarter < 1 or quarter > 4:
        raise ValueError("quarter must be 1-4")
    start_month = (quarter - 1) * 3 + 1
    start = datetime(year, start_month, 1, tzinfo=timezone.utc)
    if start_month == 10:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year, start_month + 3, 1, tzinfo=timezone.utc)
    return start, end


def compute_and_persist_aggregates(db: Session, year: int, quarter: int) -> int:
    """
    Calcule les agrégats déclaratifs pour un trimestre donné et les persiste.
    Supprime les lignes existantes pour (year, quarter) puis réinsère.
    Retourne le nombre de lignes insérées.
    """
    start_dt, end_dt = _quarter_bounds(year, quarter)

    # Supprimer les agrégats existants pour cette période
    db.execute(delete(DeclarativeAggregate).where(DeclarativeAggregate.year == year, DeclarativeAggregate.quarter == quarter))

    # Agrégats caisse : sale_items JOIN sales, période = sale_date si présent sinon created_at
    # On utilise created_at de la vente pour la période (sale_date peut être null)
    q_caisse = (
        select(
            SaleItem.category_id,
            func.coalesce(func.sum(SaleItem.weight), 0).label("weight_kg"),
            func.coalesce(func.sum(SaleItem.quantity), 0).label("quantity"),
        )
        .select_from(SaleItem)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(
            func.coalesce(Sale.sale_date, Sale.created_at) >= start_dt,
            func.coalesce(Sale.sale_date, Sale.created_at) < end_dt,
        )
        .group_by(SaleItem.category_id)
    )
    rows_caisse: List[Tuple] = list(db.execute(q_caisse).all())

    # Agrégats réception : ligne_depot, période = created_at
    q_reception = (
        select(
            LigneDepot.category_id,
            func.coalesce(func.sum(LigneDepot.poids_kg), 0).label("weight_kg"),
            func.count(LigneDepot.id).label("quantity"),
        )
        .where(
            LigneDepot.created_at >= start_dt,
            LigneDepot.created_at < end_dt,
        )
        .group_by(LigneDepot.category_id)
    )
    rows_reception: List[Tuple] = list(db.execute(q_reception).all())

    count = 0
    for category_id, weight_kg, quantity in rows_caisse:
        w = float(weight_kg) if weight_kg is not None else 0.0
        q = int(quantity) if quantity is not None else 0
        if w == 0 and q == 0:
            continue
        rec = DeclarativeAggregate(
            year=year,
            quarter=quarter,
            category_id=category_id,
            flow_type=FLOW_CAISSE,
            weight_kg=w,
            quantity=q,
        )
        db.add(rec)
        count += 1

    for category_id, weight_kg, quantity in rows_reception:
        w = float(weight_kg) if weight_kg is not None else 0.0
        q = int(quantity) if quantity is not None else 0
        if w == 0 and q == 0:
            continue
        rec = DeclarativeAggregate(
            year=year,
            quarter=quarter,
            category_id=category_id,
            flow_type=FLOW_RECEPTION,
            weight_kg=w,
            quantity=q,
        )
        db.add(rec)
        count += 1

    db.commit()
    logger.info("Declarative aggregates: persisted %s rows for %s-Q%s", count, year, quarter)
    return count


def get_aggregates(
    db: Session,
    year: int | None = None,
    quarter: int | None = None,
    flow_type: str | None = None,
    category_id: UUID | None = None,
) -> List[DeclarativeAggregate]:
    """
    Retourne les lignes d'agrégats déclaratifs selon les filtres (lecture seule).
    Utilisé par GET /aggregates et par l'export (Story 9.2).
    """
    q = select(DeclarativeAggregate).order_by(
        DeclarativeAggregate.year.desc(),
        DeclarativeAggregate.quarter.desc(),
        DeclarativeAggregate.flow_type,
        DeclarativeAggregate.category_id,
    )
    if year is not None:
        q = q.where(DeclarativeAggregate.year == year)
    if quarter is not None:
        q = q.where(DeclarativeAggregate.quarter == quarter)
    if flow_type is not None:
        q = q.where(DeclarativeAggregate.flow_type == flow_type)
    if category_id is not None:
        q = q.where(DeclarativeAggregate.category_id == category_id)
    return list(db.execute(q).scalars().all())
