from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_204_NO_CONTENT

from services.auth import get_current_user
from services.response import HTTP_404_NOT_FOUND
from models.todo import Todo_Pydantic, TodoIn_Pydantic, Todo
from models.user import User


tags = ["todos"]
router = APIRouter()


@router.post("/todos", tags=tags, response_model=Todo_Pydantic)
async def create(form_data: TodoIn_Pydantic, user: User = Depends(get_current_user)):
    todo = await Todo.create(**form_data.dict(exclude_unset=True), user=user)
    return await Todo_Pydantic.from_tortoise_orm(todo)


@router.get("/todos", tags=tags, response_model=List[Todo_Pydantic])
async def get_list(user: User = Depends(get_current_user)):
    return await Todo_Pydantic.from_queryset(Todo.filter(user=user))


@router.get("/todos/{id}", tags=tags, response_model=Todo_Pydantic, responses=HTTP_404_NOT_FOUND)
async def get_detail(id: int, user: User = Depends(get_current_user)):
    return await Todo.get_or_none(id=id, user=user)


@router.patch("/todos/{id}", tags=tags, response_model=Todo_Pydantic, responses=HTTP_404_NOT_FOUND)
async def update(id: int, form_data: TodoIn_Pydantic, user: User = Depends(get_current_user)):
    todo = await Todo.get_or_none(id=id, user=user)
    if todo:
        await todo.update_from_dict(form_data.dict(exclude_unset=True)).save()
        return await Todo_Pydantic.from_tortoise_orm(todo)


@router.delete("/todos/{id}", tags=tags, status_code=HTTP_204_NO_CONTENT)
async def delete(id: int, user: User = Depends(get_current_user)):
    deleted_count = await Todo.filter(id=id, user=user).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="Not found")
