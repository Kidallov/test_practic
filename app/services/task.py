from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.orm import Session

from app.exceptions.task_exceptions import TaskNotFound
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskUpdateSchema


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.task_repository = TaskRepository(db)

    def list_tasks(self) -> list[TaskSchema]:
        task_orm = self.task_repository.get_all()
        return [TaskSchema.model_validate(task) for task in task_orm]

    def create_task(self, task_create: TaskCreateSchema) -> TaskSchema:
        new_task = self.task_repository.create(title=task_create.title)
        self.db.commit()
        self.db.refresh(new_task)
        return TaskSchema.model_validate(new_task)

    def update_task(
        self, task_id: UUID, task_update: TaskUpdateSchema
    ) -> TaskSchema:
        task_for_update = self.task_repository.get_by_id(task_id=task_id)

        if not task_for_update:
            raise TaskNotFound('Task not found')

        if task_update.title is not None:
            task_for_update.title = task_update.title
        if task_update.completed is not None:
            task_for_update.completed = task_update.completed

        self.db.commit()
        return TaskSchema.model_validate(task_for_update)

    def delete_task(self, task_id: UUID) -> None:
        task_for_delete = self.task_repository.get_by_id(task_id=task_id)

        if not task_for_delete:
            raise TaskNotFound('Task not found')

        self.task_repository.delete(task_for_delete)
        self.db.commit()
