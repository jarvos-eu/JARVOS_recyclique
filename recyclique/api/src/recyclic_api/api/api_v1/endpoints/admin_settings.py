from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from recyclic_api.core.audit import log_admin_access
from recyclic_api.core.auth import require_role_strict
from recyclic_api.core.database import get_db
from recyclic_api.models.user import User, UserRole
from recyclic_api.schemas.admin_settings import (
    AlertThresholds,
    AlertThresholdsResponse,
    AlertThresholdsUpdate,
    CashCloseVarianceMax,
    CashCloseVarianceMaxResponse,
    CashCloseVarianceMaxUpdate,
    DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR,
)
from recyclic_api.schemas.setting import (
    SessionSettingsResponse,
    SessionSettingsUpdate,
    EmailSettingsResponse,
    EmailSettingsUpdate,
    EmailTestRequest
)
from recyclic_api.services.admin_settings_service import AdminSettingsService
from recyclic_api.services.session_settings_service import SessionSettingsService
from recyclic_api.services.email_settings_service import EmailSettingsService
from recyclic_api.core.email_service import EmailService, EmailConfigurationError
from recyclic_api.utils.rate_limit import conditional_rate_limit

router = APIRouter(tags=["admin", "settings"])

DEFAULT_THRESHOLDS = AlertThresholds(cash_discrepancy=10.0, low_inventory=5)
DEFAULT_CASH_CLOSE_VARIANCE = CashCloseVarianceMax(max_eur=DEFAULT_CASH_CLOSE_VARIANCE_MAX_EUR)


def _service(db: Session) -> AdminSettingsService:
    return AdminSettingsService(db)


@conditional_rate_limit("20/minute")
@router.get("/alert-thresholds", response_model=AlertThresholdsResponse)
def get_alert_thresholds(
    request: Request,
    site_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
) -> AlertThresholdsResponse:
    service = _service(db)
    thresholds = service.get_alert_thresholds(site_id)
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    log_admin_access(
        str(current_user.id),
        current_user.username or "Unknown",
        "/admin/settings/alert-thresholds",
        success=True,
    )
    payload = AlertThresholdsResponse(thresholds=thresholds, site_id=site_id)
    return payload.model_dump(by_alias=True)


@conditional_rate_limit("10/minute")
@router.put("/alert-thresholds", response_model=AlertThresholdsResponse)
def put_alert_thresholds(
    request: Request,
    payload: AlertThresholdsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
) -> AlertThresholdsResponse:
    service = _service(db)
    try:
        new_thresholds = service.upsert_alert_thresholds(payload.site_id, payload.thresholds)
    except ValueError as exc:
        log_admin_access(
            str(current_user.id),
            current_user.username or "Unknown",
            "/admin/settings/alert-thresholds",
            success=False,
            error_message=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    log_admin_access(
        str(current_user.id),
        current_user.username or "Unknown",
        "/admin/settings/alert-thresholds",
        success=True,
    )
    payload_response = AlertThresholdsResponse(thresholds=new_thresholds, site_id=payload.site_id)
    return payload_response.model_dump(by_alias=True)


@conditional_rate_limit("20/minute")
@router.get("/cash-close-variance-max", response_model=CashCloseVarianceMaxResponse)
def get_cash_close_variance_max(
    request: Request,
    site_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
) -> CashCloseVarianceMaxResponse:
    service = _service(db)
    max_eur = service.get_cash_close_variance_max_eur(site_id)
    log_admin_access(
        str(current_user.id),
        current_user.username or "Unknown",
        "/admin/settings/cash-close-variance-max",
        success=True,
    )
    return CashCloseVarianceMaxResponse(
        setting=CashCloseVarianceMax(max_eur=max_eur),
        site_id=site_id,
    ).model_dump(by_alias=True)


@conditional_rate_limit("10/minute")
@router.put("/cash-close-variance-max", response_model=CashCloseVarianceMaxResponse)
def put_cash_close_variance_max(
    request: Request,
    payload: CashCloseVarianceMaxUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
) -> CashCloseVarianceMaxResponse:
    service = _service(db)
    try:
        max_eur = service.upsert_cash_close_variance_max_eur(payload.site_id, payload.setting.max_eur)
    except ValueError as exc:
        log_admin_access(
            str(current_user.id),
            current_user.username or "Unknown",
            "/admin/settings/cash-close-variance-max",
            success=False,
            error_message=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    log_admin_access(
        str(current_user.id),
        current_user.username or "Unknown",
        "/admin/settings/cash-close-variance-max",
        success=True,
    )
    return CashCloseVarianceMaxResponse(
        setting=CashCloseVarianceMax(max_eur=max_eur),
        site_id=payload.site_id,
    ).model_dump(by_alias=True)


@conditional_rate_limit("20/minute")
@router.get("/session", response_model=SessionSettingsResponse)
def get_session_settings(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),
) -> SessionSettingsResponse:
    """Récupère les paramètres de session (durée d'expiration des tokens)."""
    service = SessionSettingsService(db)
    settings = service.get_session_settings()
    
    log_admin_access(
        str(current_user.id),
        current_user.username or "Unknown",
        "/admin/settings/session",
        success=True,
    )
    
    return settings


@conditional_rate_limit("10/minute")
@router.put("/session", response_model=SessionSettingsResponse)
def update_session_settings(
    request: Request,
    payload: SessionSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),
) -> SessionSettingsResponse:
    """Met à jour les paramètres de session (durée d'expiration des tokens)."""
    service = SessionSettingsService(db)

    try:
        settings = service.update_session_settings(payload)
    except ValueError as exc:
        log_admin_access(
            str(current_user.id),
            current_user.username or "Unknown",
            "/admin/settings/session",
            success=False,
            error_message=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    log_admin_access(
        str(current_user.id),
        current_user.username or "Unknown",
        "/admin/settings/session",
        success=True,
    )

    return settings


@conditional_rate_limit("20/minute")
@router.get("/email", response_model=EmailSettingsResponse)
def get_email_settings(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),
) -> EmailSettingsResponse:
    """Récupère les paramètres de configuration email (Brevo)."""
    service = EmailSettingsService(db)
    settings_data = service.get_email_settings()

    log_admin_access(
        str(current_user.id),
        current_user.username or "Unknown",
        "/admin/settings/email",
        success=True,
    )

    return EmailSettingsResponse(**settings_data)


@conditional_rate_limit("10/minute")
@router.put("/email", response_model=EmailSettingsResponse)
def update_email_settings(
    request: Request,
    payload: EmailSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),
) -> EmailSettingsResponse:
    """Met à jour les paramètres de configuration email (Brevo)."""
    service = EmailSettingsService(db)

    try:
        settings_data = service.update_email_settings(
            from_name=payload.from_name,
            from_address=payload.from_address,
            default_recipient=payload.default_recipient
        )
    except ValueError as exc:
        log_admin_access(
            str(current_user.id),
            current_user.username or "Unknown",
            "/admin/settings/email",
            success=False,
            error_message=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    log_admin_access(
        str(current_user.id),
        current_user.username or "Unknown",
        "/admin/settings/email",
        success=True,
    )

    return EmailSettingsResponse(**settings_data)


@conditional_rate_limit("5/minute")
@router.post("/email/test")
def test_email_settings(
    request: Request,
    payload: EmailTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_strict([UserRole.SUPER_ADMIN])),
) -> dict:
    """
    Envoie un email de test pour vérifier la configuration Brevo.

    Cette endpoint vérifie que:
    1. La clé API Brevo est configurée
    2. Le service email fonctionne correctement
    3. L'email peut être envoyé au destinataire spécifié
    """
    try:
        # Créer une instance du service email sans exigence de clé API
        # pour pouvoir vérifier le statut
        email_service = EmailService(require_api_key=False)

        # Vérifier si la clé API est configurée
        if not email_service.has_api_key:
            log_admin_access(
                str(current_user.id),
                current_user.username or "Unknown",
                "/admin/settings/email/test",
                success=False,
                error_message="Clé API Brevo manquante",
            )
            raise HTTPException(
                status_code=400,
                detail="La clé API Brevo n'est pas configurée. "
                       "Veuillez définir la variable d'environnement BREVO_API_KEY."
            )

        # Créer le service email avec exigence de clé API
        email_service = EmailService(require_api_key=True)

        # Récupérer les paramètres d'email depuis le service
        settings_service = EmailSettingsService(db)
        email_settings = settings_service.get_email_settings()

        # Contenu HTML du mail de test
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h1 style="color: #1976d2; margin-top: 0;">✅ Test Email - Recyclic</h1>
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">
                        Ceci est un email de test pour vérifier le service d'envoi d'emails Recyclic.
                    </p>
                    <div style="background-color: #e3f2fd; padding: 15px; border-left: 4px solid #1976d2; margin: 20px 0;">
                        <p style="margin: 0; font-weight: bold; color: #1976d2;">
                            🎉 Si vous recevez cet email, le service fonctionne correctement !
                        </p>
                    </div>
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        <strong>Configuration actuelle :</strong><br>
                        Expéditeur: {from_name} &lt;{from_address}&gt;
                    </p>
                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999; text-align: center;">
                        Email envoyé depuis Recyclic - Système de gestion pour ressourceries
                    </p>
                </div>
            </body>
        </html>
        """.format(
            from_name=email_settings["from_name"],
            from_address=email_settings["from_address"]
        )

        # Envoyer l'email de test
        success = email_service.send_email(
            to_email=payload.to_email,
            subject="🧪 Test Email - Service Recyclic",
            html_content=html_content,
            from_email=email_settings["from_address"],
            from_name=email_settings["from_name"],
            db_session=db
        )

        if success:
            log_admin_access(
                str(current_user.id),
                current_user.username or "Unknown",
                "/admin/settings/email/test",
                success=True,
            )
            return {
                "success": True,
                "message": f"Email de test envoyé avec succès à {payload.to_email}",
                "to_email": payload.to_email,
                "from_email": email_settings["from_address"],
                "from_name": email_settings["from_name"]
            }
        else:
            log_admin_access(
                str(current_user.id),
                current_user.username or "Unknown",
                "/admin/settings/email/test",
                success=False,
                error_message="Échec de l'envoi de l'email",
            )
            raise HTTPException(
                status_code=500,
                detail="Échec de l'envoi de l'email de test. Vérifiez les logs pour plus de détails."
            )

    except EmailConfigurationError as e:
        log_admin_access(
            str(current_user.id),
            current_user.username or "Unknown",
            "/admin/settings/email/test",
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) from e

    except Exception as e:
        log_admin_access(
            str(current_user.id),
            current_user.username or "Unknown",
            "/admin/settings/email/test",
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'envoi de l'email de test: {str(e)}"
        ) from e
