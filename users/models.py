from __future__ import annotations
from typing import Union
from pydantic import BaseModel
from dataclasses import dataclass

class MissingRequiredField(Exception):
    pass

@dataclass
class User:
    fullname: str
    id: Union[int, None] = None
    phone_number: Union[str, None] = None
    email: Union[str, None] = None
    created_at: Union[str, None] = None
    updated_at: Union[str, None] = None
    deleted_at: Union[str, None] = None

    def __post_init__(self):
        if self.phone_number is None and self.email is None:
            raise MissingRequiredField('Phone Number or email is required')

    def insert_dict(self) -> dict:
        return {'fullname': self.fullname, 'phone_number': self.phone_number, 'email': self.email}

    def update_dict(self) -> dict:
        return {
            'fullname': self.fullname,
            'phone_number': self.phone_number,
            'email': self.email,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at, #required for logical delete
        }
        

@dataclass
class UserResponse:
    fullname: str
    id: Union[int, None] = None
    phone_number: Union[str, None] = None
    email: Union[str, None] = None

    @classmethod
    def from_model(cls, user: User) -> UserResponse:
        return cls(
            fullname=user.fullname,
            id=user.id,
            phone_number=user.phone_number,
            email=user.email,
        )
