"""pydantic的数据模型"""
from typing import Union

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    avatarurl: Union[str, None] = None
    useremail: str
    phone: Union[str, None] = None
    isenable: bool = Field(default=False)
    username: str


class UserCreate(UserBase):
    pwd: str


class UserSession(UserBase):
    rowguid: str
