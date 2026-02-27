"""Router sales — POST/GET/PUT/PATCH ventes (Story 5.2). Push Redis pos.ticket.created apres creation."""

import json
from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from api.core.deps import require_permissions
from api.db import get_db
from api.models import (
    AuditEvent,
    CashSession,
    Category,
    PaymentTransaction,
    PresetButton,
    Sale,
    SaleItem,
    User,
)
from api.schemas.sale import (
    PaymentCreate,
    SaleCreate,
    SaleItemCreate,
    SaleItemResponse,
    SaleItemUpdate,
    SaleItemWeightUpdate,
    SaleListResponse,
    SaleNoteUpdate,
    SaleResponse,
    PaymentTransactionResponse,
)
from api.services.push_caisse import publish_ticket_created

router = APIRouter(prefix="/sales", tags=["sales"])

_CaisseOrAdmin = Depends(require_permissions("caisse.access", "caisse.virtual.access", "caisse.deferred.access", "admin"))


def _get_sale_or_404(db: Session, sale_id: UUID, load_items: bool = True) -> Sale | None:
    q = select(Sale).where(Sale.id == sale_id)
    if load_items:
        q = q.options(
            joinedload(Sale.items),
            joinedload(Sale.payment_transactions),
        )
    return db.execute(q).scalars().unique().one_or_none()


def _get_sale_item_or_404(db: Session, sale_id: UUID, item_id: UUID) -> SaleItem | None:
    return (
        db.execute(
            select(SaleItem).where(
                SaleItem.sale_id == sale_id,
                SaleItem.id == item_id,
            )
        )
        .scalars()
        .one_or_none()
    )


def _build_ticket_payload_for_redis(sale: Sale) -> dict:
    """Construit le payload ticket pour Redis (pos.ticket.created). Montants centimes, poids kg."""
    items_payload = []
    for it in sale.items:
        items_payload.append({
            "id": str(it.id),
            "category_id": str(it.category_id) if it.category_id else None,
            "preset_id": str(it.preset_id) if it.preset_id else None,
            "quantity": it.quantity,
            "unit_price": it.unit_price,
            "total_price": it.total_price,
            "weight": it.weight,
        })
    payments_payload = [
        {"id": str(pt.id), "payment_method": pt.payment_method, "amount": pt.amount}
        for pt in sale.payment_transactions
    ]
    return {
        "event": "pos.ticket.created",
        "sale_id": str(sale.id),
        "cash_session_id": str(sale.cash_session_id),
        "operator_id": str(sale.operator_id),
        "total_amount": sale.total_amount,
        "note": sale.note,
        "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
        "items": items_payload,
        "payments": payments_payload,
    }


def _sale_to_response(sale: Sale) -> SaleResponse:
    return SaleResponse(
        id=sale.id,
        cash_session_id=sale.cash_session_id,
        operator_id=sale.operator_id,
        total_amount=sale.total_amount,
        note=sale.note,
        sale_date=sale.sale_date,
        created_at=sale.created_at,
        updated_at=sale.updated_at,
        items=[SaleItemResponse.model_validate(i) for i in sale.items],
        payment_transactions=[
            PaymentTransactionResponse.model_validate(pt) for pt in sale.payment_transactions
        ],
    )


@router.post("", response_model=SaleResponse, status_code=201)
def create_sale(
    body: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> SaleResponse:
    """
    POST /v1/sales — creer un ticket (lignes + paiements).
    Refuse si cash_session invalide ou fermee ; refuse si somme payments != total lignes.
    Si offline_id fourni et deja present (ticket cree hors ligne rejoue) : retourne la vente existante (idempotence, Story 5.4).
    Apres ecriture BDD : push Redis pos.ticket.created (sauf dedup).
    """
    if body.offline_id is not None:
        existing = (
            db.execute(select(Sale).where(Sale.offline_id == body.offline_id))
            .scalars()
            .one_or_none()
        )
        if existing is not None:
            existing = _get_sale_or_404(db, existing.id, load_items=True)
            if existing:
                return _sale_to_response(existing)

    session_row = (
        db.execute(select(CashSession).where(CashSession.id == body.cash_session_id))
        .scalars()
        .one_or_none()
    )
    if not session_row:
        raise HTTPException(status_code=404, detail="Cash session not found")
    if session_row.status != "open":
        raise HTTPException(status_code=400, detail="Cash session is closed")

    total_items = 0
    for it in body.items:
        if it.unit_price is not None:
            line_total = it.unit_price * it.quantity
        elif it.total_price is not None:
            line_total = it.total_price
        else:
            raise HTTPException(
                status_code=400,
                detail="Each item must have unit_price or total_price",
            )
        total_items += line_total
        if it.category_id is None and it.preset_id is None:
            raise HTTPException(
                status_code=400,
                detail="Each item must have category_id or preset_id",
            )
        if it.category_id is not None:
            cat = db.execute(select(Category).where(Category.id == it.category_id)).scalars().one_or_none()
            if not cat:
                raise HTTPException(status_code=400, detail="Category not found")
        if it.preset_id is not None:
            preset = (
                db.execute(select(PresetButton).where(PresetButton.id == it.preset_id))
                .scalars()
                .one_or_none()
            )
            if not preset:
                raise HTTPException(status_code=400, detail="Preset not found")

    total_payments = sum(p.amount for p in body.payments)
    if total_payments != total_items:
        raise HTTPException(
            status_code=400,
            detail="Sum of payments must equal total of items",
        )

    sale = Sale(
        cash_session_id=body.cash_session_id,
        operator_id=current_user.id,
        total_amount=total_items,
        note=body.note,
        sale_date=body.sale_date,
        offline_id=body.offline_id,
    )
    db.add(sale)
    db.flush()

    for it in body.items:
        if it.unit_price is not None:
            unit = it.unit_price
            total = it.unit_price * it.quantity
        else:
            total = it.total_price or 0
            unit = it.quantity and (total // it.quantity) or 0
        item = SaleItem(
            sale_id=sale.id,
            category_id=it.category_id,
            preset_id=it.preset_id,
            quantity=it.quantity,
            unit_price=unit,
            total_price=total,
            weight=it.weight,
        )
        db.add(item)
    for p in body.payments:
        pt = PaymentTransaction(
            sale_id=sale.id,
            payment_method=p.payment_method,
            amount=p.amount,
        )
        db.add(pt)

    db.add(
        AuditEvent(
            user_id=current_user.id,
            action="sale_created",
            resource_type="sale",
            resource_id=str(sale.id),
            details=json.dumps({
                "cash_session_id": str(body.cash_session_id),
                "total_amount": total_items,
                "items_count": len(body.items),
            }),
        )
    )
    db.commit()
    db.refresh(sale)
    db.refresh(sale)  # load relationships
    sale = _get_sale_or_404(db, sale.id, load_items=True)
    if sale:
        publish_ticket_created(_build_ticket_payload_for_redis(sale))
    return _sale_to_response(sale)


@router.get("", response_model=list[SaleListResponse])
def list_sales(
    cash_session_id: UUID | None = None,
    date_from: str | None = Query(None, description="YYYY-MM-DD"),
    date_to: str | None = Query(None, description="YYYY-MM-DD"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> list[SaleListResponse]:
    """GET /v1/sales — liste avec filtres et pagination."""
    q = select(Sale)
    if cash_session_id is not None:
        q = q.where(Sale.cash_session_id == cash_session_id)
    if date_from is not None:
        try:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            q = q.where(Sale.created_at >= dt_from)
        except ValueError:
            raise HTTPException(status_code=400, detail="date_from must be YYYY-MM-DD")
    if date_to is not None:
        try:
            dt_to = datetime.strptime(date_to, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            dt_to = dt_to + timedelta(days=1)
            q = q.where(Sale.created_at < dt_to)
        except ValueError:
            raise HTTPException(status_code=400, detail="date_to must be YYYY-MM-DD")
    q = q.order_by(Sale.created_at.desc()).limit(limit).offset(offset)
    rows = db.execute(q).scalars().all()
    return [SaleListResponse.model_validate(r) for r in rows]


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> SaleResponse:
    """GET /v1/sales/{sale_id} — detail avec lignes et paiements."""
    sale = _get_sale_or_404(db, sale_id, load_items=True)
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return _sale_to_response(sale)


@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale_note(
    sale_id: UUID,
    body: SaleNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> SaleResponse:
    """PUT /v1/sales/{sale_id} — mise a jour de la note."""
    sale = _get_sale_or_404(db, sale_id, load_items=True)
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    if body.note is not None:
        sale.note = body.note
        sale.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sale)
    return _sale_to_response(sale)


@router.patch("/{sale_id}/items/{item_id}", response_model=SaleItemResponse)
def update_sale_item(
    sale_id: UUID,
    item_id: UUID,
    body: SaleItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> SaleItem:
    """PATCH /v1/sales/{sale_id}/items/{item_id} — preset_id, unit_price (editeur item admin)."""
    item = _get_sale_item_or_404(db, sale_id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Sale item not found")
    if body.preset_id is not None:
        item.preset_id = body.preset_id
    if body.unit_price is not None:
        item.unit_price = body.unit_price
        item.total_price = item.quantity * body.unit_price
    if body.preset_id is not None or body.unit_price is not None:
        item.updated_at = datetime.now(timezone.utc)
        db.add(
            AuditEvent(
                user_id=current_user.id,
                action="sale_item_updated",
                resource_type="sale_item",
                resource_id=str(item.id),
                details=json.dumps({"sale_id": str(sale_id)}),
            )
        )
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{sale_id}/items/{item_id}/weight", response_model=SaleItemResponse)
def update_sale_item_weight(
    sale_id: UUID,
    item_id: UUID,
    body: SaleItemWeightUpdate,
    db: Session = Depends(get_db),
    current_user: User = _CaisseOrAdmin,
) -> SaleItem:
    """PATCH /v1/sales/{sale_id}/items/{item_id}/weight — edition poids (admin)."""
    item = _get_sale_item_or_404(db, sale_id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Sale item not found")
    if body.weight is not None:
        item.weight = body.weight
        item.updated_at = datetime.now(timezone.utc)
        db.add(
            AuditEvent(
                user_id=current_user.id,
                action="sale_item_weight_updated",
                resource_type="sale_item",
                resource_id=str(item.id),
                details=json.dumps({"sale_id": str(sale_id), "weight": body.weight}),
            )
        )
    db.commit()
    db.refresh(item)
    return item
