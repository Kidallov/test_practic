from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from unittest.mock import Mock

    from app.services.category import CategoryService

import pytest

from app.exceptions.category_exception import CategoryNotFound
from app.models.category import CategoryORM
from app.schemas.category import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)

CATEGORY_ID_1 = UUID('00000000-0000-0000-0000-000000000001')
CATEGORY_ID_2 = UUID('00000000-0000-0000-0000-000000000002')


def test_list_categories_returns_pydantic_models(
    category_service: CategoryService,
    category_repository_mock: Mock,
) -> None:
    category_repository_mock.get_all.return_value = [
        CategoryORM(
            id=CATEGORY_ID_1,
            name='Учёба',
        ),
        CategoryORM(
            id=CATEGORY_ID_2,
            name='Работа',
        ),
    ]

    result = category_service.list_categories()

    assert result == [
        CategorySchema(
            id=CATEGORY_ID_1,
            name='Учёба',
        ),
        CategorySchema(
            id=CATEGORY_ID_2,
            name='Работа',
        ),
    ]


def test_create_category_commits_created_category(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    created_category = CategoryORM(
        id=CATEGORY_ID_1,
        name='Учёба',
    )
    category_repository_mock.create.return_value = created_category

    result = category_service.create_category(
        CategoryCreateSchema(name='Учёба')
    )

    category_repository_mock.create.assert_called_once_with(name='Учёба')
    db_mock.commit.assert_called_once_with()
    db_mock.refresh.assert_called_once_with(created_category)

    assert result.model_dump() == {
        'id': CATEGORY_ID_1,
        'name': 'Учёба',
    }


@pytest.mark.parametrize(
    ('payload', 'expected_name'),
    [
        pytest.param(
            CategoryUpdateSchema(name='Работа'),
            'Работа',
        ),
        pytest.param(
            CategoryUpdateSchema(name=None),
            'Старая категория',
        ),
    ],
)
def test_update_category_updates_only_passed_fields(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
    payload: CategoryUpdateSchema,
    expected_name: str,
) -> None:
    category = CategoryORM(
        id=CATEGORY_ID_1,
        name='Старая категория',
    )
    category_repository_mock.get_by_id.return_value = category

    result = category_service.update_category(
        CATEGORY_ID_1,
        payload,
    )

    category_repository_mock.get_by_id.assert_called_once_with(
        category_id=CATEGORY_ID_1
    )
    db_mock.commit.assert_called_once_with()

    assert result.model_dump() == {
        'id': CATEGORY_ID_1,
        'name': expected_name,
    }


def test_update_category_raises_when_category_not_found(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(CategoryNotFound):
        category_service.update_category(
            CATEGORY_ID_1,
            CategoryUpdateSchema(name='Неважно'),
        )

    db_mock.commit.assert_not_called()


def test_delete_category_deletes_category_and_commits(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category = CategoryORM(
        id=CATEGORY_ID_1,
        name='Учёба',
    )
    category_repository_mock.get_by_id.return_value = category

    category_service.delete_category(CATEGORY_ID_1)

    category_repository_mock.get_by_id.assert_called_once_with(
        category_id=CATEGORY_ID_1
    )
    category_repository_mock.delete.assert_called_once_with(category)
    db_mock.commit.assert_called_once_with()


def test_delete_category_raises_when_category_not_found(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(CategoryNotFound):
        category_service.delete_category(CATEGORY_ID_1)

    category_repository_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()
