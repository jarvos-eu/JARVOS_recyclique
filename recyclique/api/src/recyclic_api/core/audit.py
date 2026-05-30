"""
Module de gestion du journal d'audit centralisé
"""
from __future__ import annotations

import copy
import logging
from typing import Any, Dict, Optional, Union

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from recyclic_api.models.audit_log import AuditLog, AuditActionType
from recyclic_api.models.user import User

logger = logging.getLogger(__name__)

# Sous-chaînes (clés details_json) déclenchant un masquage — pas de secrets en clair en audit.
_SENSITIVE_KEY_SUBSTRINGS = (
    "password",
    "pin",
    "token",
    "secret",
    "authorization",
    "auth_header",
    "cookie",
    "refresh",
    "credential",
    "hashed_password",
    "credit_card",
    "cvv",
)


def sanitize_audit_details(details: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Retire ou masque les entrées susceptibles de contenir des secrets (best-effort, récursif léger).
    """
    if details is None:
        return None
    out: Dict[str, Any] = {}
    for key, value in details.items():
        kl = str(key).lower()
        if any(sub in kl for sub in _SENSITIVE_KEY_SUBSTRINGS):
            out[key] = "[REDACTED]"
            continue
        if isinstance(value, dict):
            out[key] = sanitize_audit_details(value) or {}
        elif isinstance(value, list):
            out[key] = [
                sanitize_audit_details(v) if isinstance(v, dict) else v for v in value
            ]
        else:
            out[key] = value
    return out


def merge_critical_audit_fields(
    details: Optional[Dict[str, Any]],
    *,
    request_id: Optional[str] = None,
    operation: Optional[str] = None,
    outcome: Optional[str] = None,
    site_id: Optional[str] = None,
    cash_register_id: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    operator_user_id: Optional[str] = None,
    device_id: Optional[str] = None,
    module_key: Optional[str] = None,
    override_active: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Schéma minimal Story 2.5 pour details_json (événements critiques caisse / terrain).

    Champs recommandés : request_id, operation, outcome, ids de contexte.
    Story 25.13 / spec 25.4 §2.4 : ``operator_user_id`` distingue l'opérateur humain ;
    ``cash_register_id`` / ``site_id`` ancrent le poste de caisse (pas interchangeables).
    """
    base = copy.deepcopy(details) if details else {}
    if request_id is not None:
        base["request_id"] = request_id
    if operation is not None:
        base["operation"] = operation
    if outcome is not None:
        base["outcome"] = outcome
    if site_id is not None:
        base["site_id"] = site_id
    if cash_register_id is not None:
        base["cash_register_id"] = cash_register_id
    if session_id is not None:
        base["session_id"] = session_id
    resolved_operator = operator_user_id if operator_user_id is not None else user_id
    if resolved_operator is not None:
        base["operator_user_id"] = resolved_operator
    if user_id is not None:
        base["user_id"] = user_id
    if device_id is not None:
        base["device_id"] = device_id
    if module_key is not None:
        base["module_key"] = module_key
    if override_active is not None:
        base["override_active"] = override_active
    return base


def log_audit(
    action_type: Union[str, AuditActionType],
    actor: Optional[User] = None,
    target_id: Optional[UUID] = None,
    target_type: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Optional[Session] = None
) -> Optional[AuditLog]:
    """
    Enregistre un événement d'audit dans le journal centralisé.
    
    Args:
        action_type: Type d'action (enum AuditActionType ou string)
        actor: Utilisateur qui a effectué l'action (optionnel)
        target_id: ID de la cible de l'action (optionnel)
        target_type: Type de la cible (ex: "user", "group", "system")
        details: Détails supplémentaires en JSON (optionnel)
        description: Description textuelle de l'action (optionnel)
        ip_address: Adresse IP de l'acteur (optionnel)
        user_agent: User-Agent de la requête (optionnel)
        db: Session de base de données (optionnel, sera créée si non fournie)
    
    Returns:
        AuditLog: L'entrée d'audit créée, ou ``None`` si aucune session DB ou si la **persistance**
        a échoué.

    Politique observabilité (inchangée côté HTTP) : en échec DB on journalise ``audit_persist_failed``
        (sans donnees sensibles), on tente ``rollback``, et **on ne propage pas** l'erreur au client :
        la requête métier peut tout de même être traitée (« fail-open » côté audit) — exploitation via
        logs et métrique ``audit_persist_failed``.
    """
    if db is None:
        # Si pas de session fournie, on ne peut pas créer l'entrée
        # Cette fonction doit être appelée dans un contexte avec une session DB
        return None
    
    try:
        # Convertir l'action_type en string si c'est un enum
        if isinstance(action_type, AuditActionType):
            action_type_str = action_type.value
        else:
            action_type_str = str(action_type)

        safe_details = sanitize_audit_details(details)
        
        # Créer l'entrée d'audit
        audit_entry = AuditLog(
            timestamp=datetime.utcnow(),
            actor_id=actor.id if actor else None,
            actor_username=actor.username if actor else None,
            action_type=action_type_str,
            target_id=target_id,
            target_type=target_type,
            details_json=safe_details,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Sauvegarder en base
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        
        return audit_entry
        
    except Exception as e:
        # Ne pas faire échouer l'opération métier ; journal structuré sans fuite de détails DB/sensibles.
        try:
            db.rollback()
        except Exception:
            pass
        logger.error(
            "audit_persist_failed action_type=%s exc_type=%s",
            action_type if isinstance(action_type, str) else getattr(action_type, "value", action_type),
            type(e).__name__,
            exc_info=True,
        )
        return None


def log_user_action(
    action_type: Union[str, AuditActionType],
    actor: User,
    target_user: Optional[User] = None,
    details: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Optional[Session] = None
) -> Optional[AuditLog]:
    """
    Version simplifiée pour les actions sur les utilisateurs.
    
    Args:
        action_type: Type d'action
        actor: Utilisateur qui effectue l'action
        target_user: Utilisateur cible (optionnel)
        details: Détails supplémentaires
        description: Description de l'action
        ip_address: Adresse IP
        user_agent: User-Agent
        db: Session de base de données
    
    Returns:
        AuditLog: L'entrée d'audit créée
    """
    return log_audit(
        action_type=action_type,
        actor=actor,
        target_id=target_user.id if target_user else None,
        target_type="user" if target_user else None,
        details=details,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        db=db
    )


def log_system_action(
    action_type: Union[str, AuditActionType],
    actor: Optional[User] = None,
    target_type: Optional[str] = None,
    target_id: Optional[UUID] = None,
    details: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Optional[Session] = None
) -> Optional[AuditLog]:
    """
    Version pour les actions système (sans utilisateur spécifique).
    
    Args:
        action_type: Type d'action
        actor: Utilisateur qui effectue l'action (optionnel)
        target_type: Type de la cible
        target_id: ID de la cible
        details: Détails supplémentaires
        description: Description de l'action
        ip_address: Adresse IP
        user_agent: User-Agent
        db: Session de base de données
    
    Returns:
        AuditLog: L'entrée d'audit créée
    """
    return log_audit(
        action_type=action_type,
        actor=actor,
        target_id=target_id,
        target_type=target_type,
        details=details,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        db=db
    )


def log_admin_access(
    user_id: str,
    username: str,
    endpoint: str,
    success: bool = True,
    error_message: Optional[str] = None,
    db: Optional[Session] = None
) -> Optional[AuditLog]:
    """
    Enregistre l'accès d'un administrateur à un endpoint.
    
    Args:
        user_id: ID de l'utilisateur administrateur
        username: Nom d'utilisateur de l'administrateur
        endpoint: Endpoint accédé
        success: Si l'accès a réussi
        error_message: Message d'erreur si échec
        db: Session de base de données
    
    Returns:
        AuditLog: L'entrée d'audit créée
    """
    action_type = (
        AuditActionType.ADMIN_ENDPOINT_ACCESS_GRANTED
        if success
        else AuditActionType.ADMIN_ENDPOINT_ACCESS_DENIED
    )
    description = f"Accès admin à {endpoint}" if success else f"Échec accès admin à {endpoint}"
    
    details = {
        "endpoint": endpoint,
        "success": success
    }
    
    if error_message:
        details["error_message"] = error_message
    
    # Note: Cette fonction ne peut pas récupérer l'utilisateur car elle est appelée
    # avant la validation, donc on passe les infos directement
    return log_audit(
        action_type=action_type,
        actor=None,  # Pas d'acteur car on n'a pas l'objet User
        details=details,
        description=description,
        db=db
    )


def log_role_change(
    admin_user_id: str,
    admin_username: str,
    target_user_id: Optional[str] = None,
    target_username: Optional[str] = None,
    old_role: Optional[str] = None,
    new_role: Optional[str] = None,
    success: bool = True,
    db: Optional[Session] = None
) -> Optional[AuditLog]:
    """
    Enregistre un changement de rôle d'utilisateur.
    
    Args:
        admin_user_id: ID de l'administrateur qui fait le changement
        admin_username: Nom d'utilisateur de l'administrateur
        target_user_id: ID de l'utilisateur cible
        target_username: Nom d'utilisateur cible
        old_role: Ancien rôle
        new_role: Nouveau rôle
        success: Si le changement a réussi
        db: Session de base de données
    
    Returns:
        AuditLog: L'entrée d'audit créée
    """
    action_type = (
        AuditActionType.USER_ROLE_CHANGED
        if success
        else AuditActionType.USER_ROLE_CHANGE_FAILED
    )
    description = f"Changement de rôle: {old_role} → {new_role}" if success else f"Échec changement de rôle"
    
    details = {
        "admin_user_id": admin_user_id,
        "admin_username": admin_username,
        "target_user_id": target_user_id,
        "target_username": target_username,
        "old_role": old_role,
        "new_role": new_role,
        "success": success
    }
    
    return log_audit(
        action_type=action_type,
        actor=None,  # Pas d'acteur car on n'a pas l'objet User
        target_id=target_user_id,
        target_type="user",
        details=details,
        description=description,
        db=db
    )


def _parse_target_uuid(value: Optional[str]) -> Optional[UUID]:
    if value is None or value == "":
        return None
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None


def log_cash_session_opening(
    user_id: str,
    username: str,
    session_id: Optional[str],
    opening_amount: float,
    success: bool = True,
    is_deferred: bool = False,
    opened_at: Optional[datetime] = None,
    created_at: Optional[datetime] = None,
    db: Optional[Session] = None,
    request_id: Optional[str] = None,
    site_id: Optional[str] = None,
    cash_register_id: Optional[str] = None,
    outcome: Optional[str] = None,
) -> Optional[AuditLog]:
    """
    Enregistre l'ouverture d'une session de caisse.
    """
    resolved_outcome = outcome or ("success" if success else "error")
    description = f"Ouverture de session de caisse {session_id}" if success else f"Échec ouverture de session de caisse"
    if is_deferred:
        description = f"Ouverture de session de caisse différée {session_id}" if success else f"Échec ouverture de session de caisse différée"
    
    details = {
        "username": username,
        "opening_amount": opening_amount,
        "success": success,
        "is_deferred": is_deferred,
    }
    
    if is_deferred and opened_at is not None:
        details["opened_at"] = opened_at.isoformat() if isinstance(opened_at, datetime) else str(opened_at)
    if is_deferred and created_at is not None:
        details["created_at"] = created_at.isoformat() if isinstance(created_at, datetime) else str(created_at)

    details = merge_critical_audit_fields(
        details,
        request_id=request_id,
        operation="cash_session.open",
        outcome=resolved_outcome,
        site_id=site_id,
        cash_register_id=cash_register_id,
        session_id=session_id or None,
        user_id=user_id,
    )
    
    return log_audit(
        action_type=AuditActionType.CASH_SESSION_OPENED,
        actor=None,
        target_id=_parse_target_uuid(session_id),
        target_type="cash_session",
        details=details,
        description=description,
        db=db
    )


def log_cash_session_closing(
    user_id: str,
    username: str,
    session_id: str,
    closing_amount: float,
    success: bool = True,
    db: Optional[Session] = None,
    request_id: Optional[str] = None,
    site_id: Optional[str] = None,
    cash_register_id: Optional[str] = None,
    outcome: Optional[str] = None,
) -> Optional[AuditLog]:
    """
    Enregistre la fermeture d'une session de caisse.

    outcome: ``success`` | ``refused`` | ``error`` — si omis, dérivé de ``success``
    (refused doit être passé explicitement, ex. accès opérateur refusé).
    """
    resolved_outcome = outcome or ("success" if success else "error")
    description = f"Fermeture de session de caisse {session_id}" if success else f"Échec fermeture de session de caisse"
    
    details = {
        "username": username,
        "closing_amount": closing_amount,
        "success": success,
    }
    details = merge_critical_audit_fields(
        details,
        request_id=request_id,
        operation="cash_session.close",
        outcome=resolved_outcome,
        site_id=site_id,
        cash_register_id=cash_register_id,
        session_id=session_id,
        user_id=user_id,
    )
    
    return log_audit(
        action_type=AuditActionType.CASH_SESSION_CLOSED,
        actor=None,
        target_id=_parse_target_uuid(session_id),
        target_type="cash_session",
        details=details,
        description=description,
        db=db
    )


def log_cash_sale(
    user_id: str,
    username: str,
    sale_id: str,
    amount: float,
    success: bool = True,
    db: Optional[Session] = None,
    request_id: Optional[str] = None,
    site_id: Optional[str] = None,
    cash_register_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Optional[AuditLog]:
    """
    Enregistre une vente en caisse (persistée localement, indépendante de toute sync aval).
    """
    resolved_outcome = "success" if success else "error"
    description = f"Vente en caisse {sale_id}" if success else f"Échec vente en caisse"
    
    details = {
        "username": username,
        "amount": amount,
        "success": success,
    }
    details = merge_critical_audit_fields(
        details,
        request_id=request_id,
        operation="cash_sale.create",
        outcome=resolved_outcome,
        site_id=site_id,
        cash_register_id=cash_register_id,
        session_id=session_id,
        user_id=user_id,
    )
    
    return log_audit(
        action_type=AuditActionType.CASH_SALE_RECORDED,
        actor=None,
        target_id=_parse_target_uuid(sale_id),
        target_type="sale",
        details=details,
        description=description,
        db=db
    )


def log_cash_session_access(
    user_id: str,
    username: str,
    session_id: str,
    success: bool = True,
    db: Optional[Session] = None,
    request_id: Optional[str] = None,
    site_id: Optional[str] = None,
    cash_register_id: Optional[str] = None,
    operation: Optional[str] = None,
    outcome: Optional[str] = None,
) -> Optional[AuditLog]:
    """
    Enregistre l'accès (lecture détail / rapport) à une session de caisse.

    ``operation`` : par défaut ``cash_session.access_detail`` ; ex. ``cash_session.report_download``.
    """
    op = operation or "cash_session.access_detail"
    resolved_outcome = outcome or ("success" if success else "error")
    description = f"Accès à la session de caisse {session_id}" if success else f"Échec accès à la session de caisse"
    
    details = {
        "username": username,
        "success": success,
    }
    details = merge_critical_audit_fields(
        details,
        request_id=request_id,
        operation=op,
        outcome=resolved_outcome,
        site_id=site_id,
        cash_register_id=cash_register_id,
        session_id=session_id,
        user_id=user_id,
    )
    
    return log_audit(
        action_type=AuditActionType.CASH_SESSION_ACCESSED,
        actor=None,
        target_id=_parse_target_uuid(session_id),
        target_type="cash_session",
        details=details,
        description=description,
        db=db
    )


def log_shared_workstation_access_refused(
    *,
    db: Optional[Session] = None,
    device_id: Optional[str] = None,
    site_id: Optional[str] = None,
    operator_user_id: Optional[str] = None,
    module_key: Optional[str] = None,
    override_active: Optional[bool] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    operation: str = "shared_workstation.access",
    outcome: str = "refused",
) -> Optional[AuditLog]:
    """Refus API poste partagé — sans opérateur actif ou device invalide."""
    details = merge_critical_audit_fields(
        {},
        request_id=request_id,
        operation=operation,
        outcome=outcome,
        site_id=site_id,
        device_id=device_id,
        module_key=module_key,
        override_active=override_active,
        user_id=user_id,
        operator_user_id=operator_user_id,
    )
    return log_audit(
        action_type=AuditActionType.SHARED_WORKSTATION_ACCESS_REFUSED,
        actor=None,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Accès poste partagé refusé",
        db=db,
    )


def log_shared_workstation_context_invalidated(
    *,
    db: Optional[Session] = None,
    device_id: Optional[str] = None,
    site_id: Optional[str] = None,
    operator_user_id: Optional[str] = None,
    module_key: Optional[str] = None,
    override_active: Optional[bool] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    reason: str = "context_change",
) -> Optional[AuditLog]:
    """Recalcul / invalidation session poste partagé."""
    details = merge_critical_audit_fields(
        {"reason": reason},
        request_id=request_id,
        operation="shared_workstation.context_invalidate",
        outcome="invalidated",
        site_id=site_id,
        device_id=device_id,
        module_key=module_key,
        override_active=override_active,
        user_id=user_id,
        operator_user_id=operator_user_id,
    )
    return log_audit(
        action_type=AuditActionType.SHARED_WORKSTATION_CONTEXT_INVALIDATED,
        actor=None,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Contexte poste partagé invalidé",
        db=db,
    )


def log_device_operator_session_started(
    *,
    db: Optional[Session] = None,
    session_id: Optional[str] = None,
    device_id: Optional[str] = None,
    site_id: Optional[str] = None,
    operator_user_id: Optional[str] = None,
    module_key: Optional[str] = None,
    override_active: Optional[bool] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {},
        request_id=request_id,
        operation="device_operator_session.start",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
        module_key=module_key,
        override_active=override_active,
        session_id=session_id,
        user_id=user_id,
        operator_user_id=operator_user_id,
    )
    return log_audit(
        action_type=AuditActionType.DEVICE_OPERATOR_SESSION_STARTED,
        actor=None,
        target_id=_parse_target_uuid(session_id),
        target_type="device_operator_session",
        details=details,
        description="Session opérateur poste démarrée",
        db=db,
    )


def log_device_operator_session_ended(
    *,
    db: Optional[Session] = None,
    session_id: Optional[str] = None,
    device_id: Optional[str] = None,
    site_id: Optional[str] = None,
    operator_user_id: Optional[str] = None,
    module_key: Optional[str] = None,
    override_active: Optional[bool] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    reason: str = "ended",
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {"reason": reason},
        request_id=request_id,
        operation="device_operator_session.end",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
        module_key=module_key,
        override_active=override_active,
        session_id=session_id,
        user_id=user_id,
        operator_user_id=operator_user_id,
    )
    return log_audit(
        action_type=AuditActionType.DEVICE_OPERATOR_SESSION_ENDED,
        actor=None,
        target_id=_parse_target_uuid(session_id),
        target_type="device_operator_session",
        details=details,
        description="Session opérateur poste terminée",
        db=db,
    )


def log_shared_workstation_pin_success(
    *,
    db: Optional[Session] = None,
    device_id: Optional[str] = None,
    operator_user_id: Optional[str] = None,
    site_id: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {},
        request_id=request_id,
        operation="shared_workstation.pin_verify",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
        session_id=session_id,
        user_id=user_id,
        operator_user_id=operator_user_id,
    )
    return log_audit(
        action_type=AuditActionType.SHARED_WORKSTATION_PIN_SUCCESS,
        actor=None,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="PIN poste partagé validé",
        db=db,
    )


def log_shared_workstation_pin_failure(
    *,
    db: Optional[Session] = None,
    device_id: Optional[str] = None,
    operator_user_id: Optional[str] = None,
    site_id: Optional[str] = None,
    outcome: str = "invalid",
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {"failure_kind": outcome},
        request_id=request_id,
        operation="shared_workstation.pin_verify",
        outcome="failure",
        site_id=site_id,
        device_id=device_id,
        operator_user_id=operator_user_id,
    )
    return log_audit(
        action_type=AuditActionType.SHARED_WORKSTATION_PIN_FAILURE,
        actor=None,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Échec vérification PIN poste partagé",
        db=db,
    )


def log_shared_workstation_pin_lockout(
    *,
    db: Optional[Session] = None,
    device_id: Optional[str] = None,
    operator_user_id: Optional[str] = None,
    site_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {},
        request_id=request_id,
        operation="shared_workstation.pin_lockout",
        outcome="lockout",
        site_id=site_id,
        device_id=device_id,
        operator_user_id=operator_user_id,
    )
    return log_audit(
        action_type=AuditActionType.SHARED_WORKSTATION_PIN_LOCKOUT,
        actor=None,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Verrouillage PIN poste partagé",
        db=db,
    )


def log_shared_workstation_pin_lockout_cleared(
    *,
    db: Optional[Session] = None,
    actor: Optional[User] = None,
    device_id: str,
    operator_user_id: str,
    site_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {},
        request_id=request_id,
        operation="shared_workstation.pin_lockout_clear",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
        operator_user_id=operator_user_id,
        user_id=str(actor.id) if actor is not None else None,
    )
    return log_audit(
        action_type=AuditActionType.SHARED_WORKSTATION_PIN_LOCKOUT_CLEARED,
        actor=actor,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Déblocage lockout PIN poste partagé",
        db=db,
    )


def log_registered_device_created(
    *,
    db: Optional[Session] = None,
    actor: Optional[User] = None,
    device_id: str,
    site_id: Optional[str] = None,
    module_keys: Optional[list[str]] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    """Création admin d'un poste partagé enregistré."""
    extra: Dict[str, Any] = {}
    if module_keys is not None:
        extra["allowed_module_keys"] = list(module_keys)
    details = merge_critical_audit_fields(
        extra,
        request_id=request_id,
        operation="registered_device.create",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
    )
    return log_audit(
        action_type=AuditActionType.REGISTERED_DEVICE_CREATED,
        actor=actor,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Poste partagé créé",
        db=db,
    )


def log_registered_device_updated(
    *,
    db: Optional[Session] = None,
    actor: Optional[User] = None,
    device_id: str,
    site_id: Optional[str] = None,
    module_keys: Optional[list[str]] = None,
    changed_fields: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    """Mise à jour admin d'un poste partagé — champs modifiés dans details_json."""
    extra: Dict[str, Any] = {}
    if changed_fields:
        extra["changed_fields"] = changed_fields
    if module_keys is not None:
        extra["allowed_module_keys"] = list(module_keys)
    details = merge_critical_audit_fields(
        extra,
        request_id=request_id,
        operation="registered_device.update",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
    )
    return log_audit(
        action_type=AuditActionType.REGISTERED_DEVICE_UPDATED,
        actor=actor,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Poste partagé mis à jour",
        db=db,
    )


def log_registered_device_revoked(
    *,
    db: Optional[Session] = None,
    actor: Optional[User] = None,
    device_id: str,
    site_id: Optional[str] = None,
    reason: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    """Révocation admin d'un poste partagé."""
    extra: Dict[str, Any] = {}
    if reason:
        extra["reason"] = reason
    details = merge_critical_audit_fields(
        extra,
        request_id=request_id,
        operation="registered_device.revoke",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
    )
    return log_audit(
        action_type=AuditActionType.REGISTERED_DEVICE_REVOKED,
        actor=actor,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Poste partagé révoqué",
        db=db,
    )


def log_device_enrollment_code_issued(
    *,
    db: Optional[Session] = None,
    actor: Optional[User] = None,
    device_id: str,
    purpose: str,
    site_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {"purpose": purpose},
        request_id=request_id,
        operation="device_enrollment.issue_code",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
    )
    return log_audit(
        action_type=AuditActionType.DEVICE_ENROLLMENT_CODE_ISSUED,
        actor=actor,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Code d'enrôlement émis",
        db=db,
    )


def log_device_enrolled(
    *,
    db: Optional[Session] = None,
    device_id: str,
    site_id: Optional[str] = None,
    purpose: str,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {"purpose": purpose},
        request_id=request_id,
        operation="device_enrollment.complete",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
    )
    action = AuditActionType.DEVICE_ENROLLED
    if purpose == "reconnect":
        action = AuditActionType.DEVICE_RECONNECTED
    elif purpose == "replace":
        action = AuditActionType.DEVICE_REPLACED
    return log_audit(
        action_type=action,
        actor=None,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Enrôlement poste complété",
        db=db,
    )


def log_device_identity_conflict(
    *,
    db: Optional[Session] = None,
    device_id: str,
    site_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {},
        request_id=request_id,
        operation="device_credential.verify",
        outcome="conflict",
        site_id=site_id,
        device_id=device_id,
    )
    return log_audit(
        action_type=AuditActionType.DEVICE_IDENTITY_CONFLICT,
        actor=None,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Conflit identité poste détecté",
        db=db,
    )


def log_device_identity_lost_marked(
    *,
    db: Optional[Session] = None,
    actor: Optional[User] = None,
    device_id: str,
    site_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    details = merge_critical_audit_fields(
        {},
        request_id=request_id,
        operation="device_enrollment.mark_identity_lost",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
    )
    return log_audit(
        action_type=AuditActionType.DEVICE_IDENTITY_LOST_MARKED,
        actor=actor,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Identité locale marquée perdue",
        db=db,
    )


def log_device_conflict_resolved(
    *,
    db: Optional[Session] = None,
    actor: Optional[User] = None,
    device_id: str,
    action: str,
    site_id: Optional[str] = None,
    distinct_device_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Optional[AuditLog]:
    extra: Dict[str, Any] = {"action": action}
    if distinct_device_id:
        extra["distinct_device_id"] = distinct_device_id
    details = merge_critical_audit_fields(
        extra,
        request_id=request_id,
        operation="device_enrollment.resolve_conflict",
        outcome="success",
        site_id=site_id,
        device_id=device_id,
    )
    return log_audit(
        action_type=AuditActionType.DEVICE_CONFLICT_RESOLVED,
        actor=actor,
        target_id=_parse_target_uuid(device_id),
        target_type="registered_device",
        details=details,
        description="Conflit poste résolu",
        db=db,
    )
