from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException

class CategoryCreate(BaseModel):
    title: str

class Category(CategoryCreate):
    id: int

class CategoryUpdate(Category):
    title: str | None = None

app = FastAPI()

categories: list[Category] = []

@app.post('/categories/', response_model=Category, status_code=201)
def create_category(category: CategoryCreate):
    new_id = len(categories) + 1
    category_data = Category(id=new_id, **category.model_dump())
    categories.append(category_data)
    return category_data

@app.get('/categories/')
def get_category():
    return categories

@app.patch('/categories/{category_id}', response_model=Category)
def update_category(category_id: int, category: CategoryUpdate):

    сategory_index = None
    for i, item in enumerate(categories):
        if item.id == category_id:
            сategory_index = i
            break

    if сategory_index is None:
        raise HTTPException(status_code=404, detail="Category not found")

    stored_category = categories[сategory_index]

    update_data = category.model_dump(exclude_unset=True)

    updated_category = stored_category.model_copy(update=update_data)
    categories[сategory_index] = updated_category

    return updated_category

@app.delete('/categories/{category_id}', status_code=204)
def delete_category(category_id: int):

    сategory_index = None
    for i, item in enumerate(categories):
        if item.id == category_id:
            сategory_index = i
            break

    if сategory_index is None:
            raise HTTPException(status_code=404, detail="Category not found")

    del categories[сategory_index]
    return None