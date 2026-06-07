import json
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from recyclic_api.models.admin_setting import AdminSetting
from recyclic_api.schemas.admin_settings import AlertThresholds
from recyclic_api.utils.financial_security import encrypt_string, decrypt_string, FinancialDataError

def get_close_variance_max_eur(db: Session, site_id: Optional[str | UUID]) -> float:
    """Seuil max |écart espèces| autorisé à la clôture pour un site (défaut 2,00 €)."""
    sid = str(site_id) if site_id is not None else None
    return AdminSettingsService(db).get_cash_close_variance_max_eur(sid)


class AdminSettingsService:
    """Service helper to persist encrypted administrative settings."""

    ALERT_KEY = "alert_thresholds"
    CASH_CLOSE_VARIANCE_MAX_KEY = "cash_close_variance_max_eur"
    DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR = 2.0

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _normalise_site_id(site_id: Optional[str]) -> Optional[UUID]:
        if site_id in (None, ""):
            return None
        if isinstance(site_id, UUID):
            return site_id
        try:
            return UUID(str(site_id))
        except (TypeError, ValueError) as exc:
            raise ValueError("site_id doit être un UUID valide") from exc

    def _build_query(self, key: str, site_id: Optional[str]):
        query = self.db.query(AdminSetting).filter(AdminSetting.key == key)
        normalised = self._normalise_site_id(site_id)
        if normalised is None:
            query = query.filter(AdminSetting.site_id.is_(None))
        else:
            query = query.filter(AdminSetting.site_id == normalised)
        return query, normalised

    def get_alert_thresholds(self, site_id: Optional[str]) -> Optional[AlertThresholds]:
        query, _ = self._build_query(self.ALERT_KEY, site_id)
        record = query.first()
        if not record:
            return None
        try:
            payload = decrypt_string(record.value_encrypted)
        except FinancialDataError:
            return None
        data = json.loads(payload)
        return AlertThresholds.model_validate(data)

    def upsert_alert_thresholds(self, site_id: Optional[str], thresholds: AlertThresholds) -> AlertThresholds:
        payload = json.dumps(thresholds.model_dump())
        encrypted = encrypt_string(payload)

        query, normalised_site = self._build_query(self.ALERT_KEY, site_id)
        record = query.first()

        if record:
            record.value_encrypted = encrypted
        else:
            record = AdminSetting(
                key=self.ALERT_KEY,
                site_id=normalised_site,
                value_encrypted=encrypted,
            )
            self.db.add(record)

        self.db.commit()
        self.db.refresh(record)
        return thresholds

    def get_cash_close_variance_max_eur(self, site_id: Optional[str]) -> float:
        query, _ = self._build_query(self.CASH_CLOSE_VARIANCE_MAX_KEY, site_id)
        record = query.first()
        if not record:
            return self.DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR
        encrypted = getattr(record, "value_encrypted", None)
        if not isinstance(encrypted, str):
            return self.DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR
        try:
            payload = decrypt_string(encrypted)
            data = json.loads(payload)
            val = float(data.get("max_eur", self.DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR))
            return val if val > 0 else self.DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR
        except (FinancialDataError, TypeError, ValueError, json.JSONDecodeError):
            return self.DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR

    def upsert_cash_close_variance_max_eur(self, site_id: Optional[str], max_eur: float) -> float:
        if max_eur <= 0 or max_eur > 500:
            raise ValueError("max_eur doit être compris entre 0 (exclus) et 500")
        payload = json.dumps({"max_eur": float(max_eur)})
        encrypted = encrypt_string(payload)
        query, normalised_site = self._build_query(self.CASH_CLOSE_VARIANCE_MAX_KEY, site_id)
        record = query.first()
        if record:
            record.value_encrypted = encrypted
        else:
            record = AdminSetting(
                key=self.CASH_CLOSE_VARIANCE_MAX_KEY,
                site_id=normalised_site,
                value_encrypted=encrypted,
            )
            self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return float(max_eur)

