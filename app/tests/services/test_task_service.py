from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from unittest.mock import Mock

    from app.services.task import TaskService

import pytest

from app.exceptions.task_exceptions import TaskNotFound
from app.models.task import TaskORM
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskUpdateSchema

TASK_ID_1 = UUID('00000000-0000-0000-0000-000000000001')
TASK_ID_2 = UUID('00000000-0000-0000-0000-000000000002')


def test_list_tasks_returns_pydantic_models(
    service: TaskService,
    repository_mock: Mock,
) -> None:
    # Имитируем, что метод get_all репозитория вернет эти задачи
    repository_mock.get_all.return_value = [
        TaskORM(id=TASK_ID_1, title='Изучить pytest', completed=False),
        TaskORM(id=TASK_ID_2, title='Написать первый тест', completed=True),
    ]

    result = service.list_tasks()

    assert result == [
        TaskSchema(id=TASK_ID_1, title='Изучить pytest', completed=False),
        TaskSchema(id=TASK_ID_2, title='Написать первый тест', completed=True),
    ]


def test_create_task_commits_created_task(
    service: TaskService,
    db_mock: Mock,
    repository_mock: Mock,
) -> None:
    created_task = TaskORM(id=TASK_ID_1, title='Новая задача', completed=False)
    repository_mock.create.return_value = created_task

    result = service.create_task(TaskCreateSchema(title='Новая задача'))

    repository_mock.create.assert_called_once_with(title='Новая задача')
    db_mock.commit.assert_called_once_with()
    assert result.model_dump() == {
        'id': TASK_ID_1,
        'title': 'Новая задача',
        'completed': False,
    }


@pytest.mark.parametrize(
    ('payload', 'expected_title', 'expected_completed'),
    [
        pytest.param(
            TaskUpdateSchema(title='Обновить заголовок'),  # payload
            'Обновить заголовок',  # expected_title
            False,  # expected_completed
        ),
        pytest.param(
            TaskUpdateSchema(completed=True),  # payload
            'Старая задача',  # expected_title
            True,  # expected_completed
        ),
        pytest.param(
            TaskUpdateSchema(title='Готово', completed=True),  # payload
            'Готово',  # expected_title
            True,  # expected_completed
        ),
    ],
)
def test_update_task_updates_only_passed_fields(
    service: TaskService,
    db_mock: Mock,
    repository_mock: Mock,
    payload: TaskUpdateSchema,
    expected_title: str,
    expected_completed: bool,
) -> None:
    task = TaskORM(id=TASK_ID_1, title='Старая задача', completed=False)
    repository_mock.get_by_id.return_value = task

    result = service.update_task(TASK_ID_1, payload)

    repository_mock.get_by_id.assert_called_once_with(task_id=TASK_ID_1)
    db_mock.commit.assert_called_once_with()
    assert result.model_dump() == {
        'id': TASK_ID_1,
        'title': expected_title,
        'completed': expected_completed,
    }


def test_update_task_raises_when_task_not_found(
    service: TaskService,
    db_mock: Mock,
    repository_mock: Mock,
) -> None:
    repository_mock.get_by_id.return_value = None

    with pytest.raises(TaskNotFound):  # Должна произойти указанная ошибка
        service.update_task(TASK_ID_1, TaskUpdateSchema(title='Неважно'))

    db_mock.commit.assert_not_called()
