# Schemas Pydantic — Admin users (Story 8.1).
# Liste, détail, pending, actions (role, status, groupes, approve, reject, reset password/PIN).

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AdminUserListResponse(BaseModel):
    """Un utilisateur dans la liste GET /v1/admin/users."""

    id: UUID
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    role: str
    status: str
    site_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminUserDetailResponse(BaseModel):
    """Détail utilisateur GET /v1/admin/users/{user_id} (avec group_ids)."""

    id: UUID
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    role: str
    status: str
    site_id: UUID | None
    created_at: datetime
    updated_at: datetime
    group_ids: list[UUID] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class AdminPendingUserResponse(BaseModel):
    """Inscription en attente GET /v1/admin/users/pending (registration_request)."""

    id: UUID
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    status: str
    requested_at: datetime

    model_config = {"from_attributes": True}


class AdminUserRoleUpdate(BaseModel):
    role: str = Field(..., min_length=1, max_length=64)


class AdminUserStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=32)


class AdminUserProfileUpdate(BaseModel):
    """PUT /v1/admin/users/{user_id} — champs modifiables."""

    first_name: str | None = Field(None, max_length=128)
    last_name: str | None = Field(None, max_length=128)
    email: str | None = Field(None, min_length=1)
    role: str | None = Field(None, max_length=64)
    status: str | None = Field(None, max_length=32)
    site_id: UUID | None = None


class AdminUserGroupsUpdate(BaseModel):
    group_ids: list[UUID] = Field(default_factory=list, max_length=100)


class AdminApproveRejectBody(BaseModel):
    """Approve/Reject : id = registration_request id pour pending."""

    registration_request_id: UUID


class AdminUserCreate(BaseModel):
    """POST /v1/users — création utilisateur par admin (Story 8.1)."""

    username: str = Field(..., min_length=1, max_length=128)
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
    first_name: str | None = Field(None, max_length=128)
    last_name: str | None = Field(None, max_length=128)
    role: str = Field(default="operator", max_length=64)
    status: str = Field(default="active", max_length=32)
    site_id: UUID | None = None


class AuditEventResponse(BaseModel):
    """Événement audit GET /v1/admin/users/{user_id}/history."""

    id: UUID
    timestamp: datetime
    user_id: UUID | None
    action: str
    resource_type: str | None
    resource_id: str | None
    details: str | None

    model_config = {"from_attributes": True}


class AdminUsersStatusesResponse(BaseModel):
    """GET /v1/admin/users/statuses — user_ids ayant une session active (en ligne)."""

    online_user_ids: list[UUID] = Field(default_factory=list)


class AdminResetPasswordBody(BaseModel):
    new_password: str = Field(..., min_length=8)


class AdminResetPinBody(BaseModel):
    new_pin: str = Field(..., min_length=4, max_length=8)
