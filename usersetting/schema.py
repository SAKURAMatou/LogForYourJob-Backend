"""pydantic的数据模型"""
from typing import Union, Optional

from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    avatarurl: Union[str, None] = None
    useremail: str
    phone: Union[str, None] = None
    isenable: bool = Field(default=False)
    username: str


class UserCreate(UserBase):
    pwd: str


class UserLogin(BaseModel):
    name: str
    pwd: str


class UserSession(UserBase):
    rowguid: str


class UserBasicInfoEdit(BaseModel):
    """用户基本信息修改入参"""
    name: Optional[str] = None
    email: Optional[str] = None
    avatarguid: Optional[str] = None

    @field_validator("name", 'email', 'avatarguid', mode='before')
    def empty_str_to_none(cls, v):
        return None if v == "" else v
