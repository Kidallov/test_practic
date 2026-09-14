from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.orm import Session

from app.exceptions.category_exception import CategoryNotFound
from app.repositories.category import CategoryRepository
from app.schemas.category import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)


class CategoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.category_repository = CategoryRepository(db)

    def list_categories(self) -> list[CategorySchema]:
        category_orm = self.category_repository.get_all()
        return [
            CategorySchema.model_validate(category)
            for category in category_orm
        ]

    def create_category(
        self, category_create: CategoryCreateSchema
    ) -> CategorySchema:
        new_category = self.category_repository.create(
            name=category_create.name
        )
        self.db.commit()
        self.db.refresh(new_category)
        return CategorySchema.model_validate(new_category)

    def update_category(
        self, category_id: UUID, category_update: CategoryUpdateSchema
    ) -> CategorySchema:
        category_for_update = self.category_repository.get_by_id(
            category_id=category_id
        )

        if not category_for_update:
            raise CategoryNotFound('Task not found')

        if category_update.name is not None:
            category_for_update.name = category_update.name

        self.db.commit()
        return CategorySchema.model_validate(category_for_update)

    def delete_category(self, category_id: UUID) -> None:
        category_for_delete = self.category_repository.get_by_id(
            category_id=category_id
        )

        if not category_for_delete:
            raise CategoryNotFound('Category not found')

        self.category_repository.delete(category_for_delete)
        self.db.commit()
