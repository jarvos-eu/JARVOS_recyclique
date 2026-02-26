# Schemas Pydantic — Categories (Story 2.3). Requêtes/réponses en snake_case.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: UUID | None = None
    official_name: str | None = Field(None, max_length=512)
    is_visible_sale: bool = True
    is_visible_reception: bool = True
    display_order: int = 0
    display_order_entry: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    parent_id: UUID | None = None
    official_name: str | None = Field(None, max_length=512)
    is_visible_sale: bool | None = None
    is_visible_reception: bool | None = None
    display_order: int | None = None
    display_order_entry: int | None = None


class CategoryResponse(CategoryBase):
    id: UUID
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategoryHierarchyNode(BaseModel):
    """Noeud d'arborescence pour GET /categories/hierarchy."""

    id: UUID
    name: str
    parent_id: UUID | None
    official_name: str | None
    is_visible_sale: bool
    is_visible_reception: bool
    display_order: int
    display_order_entry: int
    deleted_at: datetime | None
    children: list["CategoryHierarchyNode"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


CategoryHierarchyNode.model_rebuild()


class CategoryVisibilityUpdate(BaseModel):
    """Body pour PUT /categories/{id}/visibility."""

    is_visible_sale: bool | None = None
    is_visible_reception: bool | None = None


class CategoryDisplayOrderUpdate(BaseModel):
    """Body pour PUT /categories/{id}/display-order."""

    display_order: int | None = None
    display_order_entry: int | None = None
