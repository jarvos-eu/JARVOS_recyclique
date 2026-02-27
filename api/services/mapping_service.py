# Service de resolution RecyClique -> Paheko (Story 7.1).
# Utilise par le worker push et la logique de cloture pour obtenir les identifiants Paheko.
# CRUD (Story 7.2) : create/update/delete pour les routes admin avec audit.
# Config Paheko = reference (NFR-I2) ; les mappings pointent vers des identifiants existants.

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import (
    Category,
    CategoryMapping,
    CashRegister,
    LocationMapping,
    PaymentMethodMapping,
    Site,
)


def resolve_payment_method(db: Session, recyclic_code: str) -> int | None:
    """
    Resout un code moyen de paiement RecyClique -> id_method Paheko (plugin_pos_methods.id).
    Retourne None si aucun mapping.
    """
    row = db.execute(
        select(PaymentMethodMapping.paheko_id_method).where(
            PaymentMethodMapping.recyclic_code == recyclic_code
        )
    ).scalars().one_or_none()
    return row[0] if row else None


def resolve_category(db: Session, category_id: UUID) -> int | None:
    """
    Resout un category_id RecyClique -> paheko_category_id (plugin_pos_categories.id).
    Retourne None si aucun mapping.
    """
    row = db.execute(
        select(CategoryMapping.paheko_category_id).where(
            CategoryMapping.category_id == category_id
        )
    ).scalars().one_or_none()
    return row[0] if row else None


def resolve_location_by_site(db: Session, site_id: UUID) -> int | None:
    """
    Resout un site_id RecyClique -> paheko_id_location (plugin_pos_locations.id).
    Retourne None si aucun mapping pour ce site.
    """
    row = db.execute(
        select(LocationMapping.paheko_id_location).where(
            LocationMapping.site_id == site_id
        )
    ).scalars().one_or_none()
    return row[0] if row else None


def resolve_location_by_register(db: Session, register_id: UUID) -> int | None:
    """
    Resout un register_id RecyClique -> paheko_id_location (plugin_pos_locations.id).
    Retourne None si aucun mapping pour ce poste. Si pas de mapping register,
    on peut fallback sur le site du register (non implemente ici pour garder la resolution explicite).
    """
    row = db.execute(
        select(LocationMapping.paheko_id_location).where(
            LocationMapping.register_id == register_id
        )
    ).scalars().one_or_none()
    return row[0] if row else None


def resolve_location(db: Session, site_id: UUID | None = None, register_id: UUID | None = None) -> int | None:
    """
    Resout site ou register -> paheko_id_location. Priorite : register_id si fourni, sinon site_id.
    Retourne None si aucun mapping trouve.
    """
    if register_id is not None:
        loc = resolve_location_by_register(db, register_id)
        if loc is not None:
            return loc
    if site_id is not None:
        return resolve_location_by_site(db, site_id)
    return None


# ----- CRUD payment method mapping (Story 7.2) -----


def create_payment_method_mapping(
    db: Session,
    *,
    recyclic_code: str,
    paheko_id_method: int,
) -> PaymentMethodMapping:
    """Cree un mapping moyen de paiement. Leve ValueError si recyclic_code deja existant."""
    existing = db.execute(
        select(PaymentMethodMapping).where(PaymentMethodMapping.recyclic_code == recyclic_code)
    ).scalars().one_or_none()
    if existing:
        raise ValueError("A mapping for this recyclic_code already exists")
    mapping = PaymentMethodMapping(recyclic_code=recyclic_code, paheko_id_method=paheko_id_method)
    db.add(mapping)
    db.flush()
    return mapping


def update_payment_method_mapping(
    db: Session,
    mapping_id: UUID,
    *,
    paheko_id_method: int | None = None,
) -> PaymentMethodMapping | None:
    """Met a jour un mapping. Retourne None si non trouve."""
    mapping = db.execute(
        select(PaymentMethodMapping).where(PaymentMethodMapping.id == mapping_id)
    ).scalars().one_or_none()
    if mapping is None:
        return None
    if paheko_id_method is not None:
        mapping.paheko_id_method = paheko_id_method
    mapping.updated_at = datetime.now(timezone.utc)
    db.flush()
    return mapping


def delete_payment_method_mapping(db: Session, mapping_id: UUID) -> bool:
    """Supprime un mapping. Retourne True si supprime, False si non trouve."""
    mapping = db.execute(
        select(PaymentMethodMapping).where(PaymentMethodMapping.id == mapping_id)
    ).scalars().one_or_none()
    if mapping is None:
        return False
    db.delete(mapping)
    db.flush()
    return True


# ----- CRUD category mapping (Story 7.2) -----


def create_category_mapping(
    db: Session,
    *,
    category_id: UUID,
    paheko_category_id: int | None = None,
    paheko_code: str | None = None,
) -> CategoryMapping:
    """Cree un mapping categorie. Leve ValueError si category non trouvee ou deja mappee."""
    if paheko_category_id is None and (paheko_code is None or not paheko_code.strip()):
        raise ValueError("At least one of paheko_category_id or paheko_code must be set")
    category = db.execute(select(Category).where(Category.id == category_id)).scalars().one_or_none()
    if category is None:
        raise ValueError("Category not found")
    existing = db.execute(
        select(CategoryMapping).where(CategoryMapping.category_id == category_id)
    ).scalars().one_or_none()
    if existing:
        raise ValueError("A mapping for this category already exists")
    mapping = CategoryMapping(
        category_id=category_id,
        paheko_category_id=paheko_category_id,
        paheko_code=paheko_code,
    )
    db.add(mapping)
    db.flush()
    return mapping


def update_category_mapping(
    db: Session,
    mapping_id: UUID,
    *,
    paheko_category_id: int | None = None,
    paheko_code: str | None = None,
) -> CategoryMapping | None:
    """Met a jour un mapping categorie. Retourne None si non trouve."""
    mapping = db.execute(
        select(CategoryMapping).where(CategoryMapping.id == mapping_id)
    ).scalars().one_or_none()
    if mapping is None:
        return None
    if paheko_category_id is not None:
        mapping.paheko_category_id = paheko_category_id
    if paheko_code is not None:
        mapping.paheko_code = paheko_code
    mapping.updated_at = datetime.now(timezone.utc)
    db.flush()
    return mapping


def delete_category_mapping(db: Session, mapping_id: UUID) -> bool:
    """Supprime un mapping categorie. Retourne True si supprime, False si non trouve."""
    mapping = db.execute(
        select(CategoryMapping).where(CategoryMapping.id == mapping_id)
    ).scalars().one_or_none()
    if mapping is None:
        return False
    db.delete(mapping)
    db.flush()
    return True


# ----- CRUD location mapping (Story 7.2) -----


def create_location_mapping(
    db: Session,
    *,
    site_id: UUID | None = None,
    register_id: UUID | None = None,
    paheko_id_location: int,
) -> LocationMapping:
    """Cree un mapping site/emplacement. Exactement un de site_id ou register_id. Leve ValueError si invalide."""
    if (site_id is None) == (register_id is None):
        raise ValueError("Exactly one of site_id or register_id must be set")
    if site_id is not None:
        site = db.execute(select(Site).where(Site.id == site_id)).scalars().one_or_none()
        if site is None:
            raise ValueError("Site not found")
        existing = db.execute(
            select(LocationMapping).where(LocationMapping.site_id == site_id)
        ).scalars().one_or_none()
        if existing:
            raise ValueError("A mapping for this site already exists")
        mapping = LocationMapping(site_id=site_id, paheko_id_location=paheko_id_location)
    else:
        reg = db.execute(
            select(CashRegister).where(CashRegister.id == register_id)
        ).scalars().one_or_none()
        if reg is None:
            raise ValueError("Cash register not found")
        existing = db.execute(
            select(LocationMapping).where(LocationMapping.register_id == register_id)
        ).scalars().one_or_none()
        if existing:
            raise ValueError("A mapping for this register already exists")
        mapping = LocationMapping(
            register_id=register_id,
            paheko_id_location=paheko_id_location,
        )
    db.add(mapping)
    db.flush()
    return mapping


def update_location_mapping(
    db: Session,
    mapping_id: UUID,
    *,
    paheko_id_location: int | None = None,
) -> LocationMapping | None:
    """Met a jour un mapping location. Retourne None si non trouve."""
    mapping = db.execute(
        select(LocationMapping).where(LocationMapping.id == mapping_id)
    ).scalars().one_or_none()
    if mapping is None:
        return None
    if paheko_id_location is not None:
        mapping.paheko_id_location = paheko_id_location
    mapping.updated_at = datetime.now(timezone.utc)
    db.flush()
    return mapping


def delete_location_mapping(db: Session, mapping_id: UUID) -> bool:
    """Supprime un mapping location. Retourne True si supprime, False si non trouve."""
    mapping = db.execute(
        select(LocationMapping).where(LocationMapping.id == mapping_id)
    ).scalars().one_or_none()
    if mapping is None:
        return False
    db.delete(mapping)
    db.flush()
    return True
