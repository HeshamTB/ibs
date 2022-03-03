from typing import Optional

from pydantic import BaseModel


class IotEntityBase(BaseModel):
    id: int
    description: str


class IotEntityCreate(IotEntityBase):
    pass


class IotEntity(IotEntityBase):
    id: int
    description: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    authorized_devices: list[IotEntity] = []

    class Config:
        orm_mode = True
