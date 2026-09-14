from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from app.schemas.task import TaskCreateSchema, TaskSchema, TaskUpdateSchema
    from app.services.task import TaskService

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.depends import get_task_service
from app.exceptions.task_exceptions import TaskNotFound

router = APIRouter(prefix='/tasks')


@router.get('')
def get_tasks(
    task_service: TaskService = Depends(get_task_service),
) -> list[TaskSchema]:
    return task_service.list_tasks()


@router.post('', status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreateSchema,
    task_service: TaskService = Depends(get_task_service),
) -> TaskSchema:
    return task_service.create_task(task_create=payload)


@router.patch('/{task_id}')
def update_task(
    task_id: UUID,
    payload: TaskUpdateSchema,
    task_service: TaskService = Depends(get_task_service),
) -> TaskSchema:
    try:
        return task_service.update_task(task_id=task_id, task_update=payload)
    except TaskNotFound as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from err


@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service),
) -> None:
    try:
        return task_service.delete_task(task_id=task_id)
    except TaskNotFound as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from err
