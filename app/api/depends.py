from typing import TYPE_CHECKING

from fastapi import Depends

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.category import CategoryService
from app.services.task import TaskService


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Функция для получения экземпляра TaskService"""
    return TaskService(db)


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    """Функция для получения экземпляра CategoryService"""
    return CategoryService(db)
