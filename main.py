from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union, List, List
from dataclasses import dataclass, field
from users.service import (
    get_users,
    get_user_by_id,
    insert_user,
)
from users.models import User

app = FastAPI()

@app.get('/users')
async def get_users_endpoint() -> List[User]:
    return get_users()

@app.get('/users/{user_id')
async def get_user_by_id_enpoint(user_id: int) -> User:
    return get_user_by_id(user_id)

@app.post('/users')
async def new_user_endpoint(user: User) -> User:
    return insert_user(user)
