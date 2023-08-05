"""logforjob的pydantic模型"""
from datetime import datetime, date
from typing import Optional, Union
from pydantic import BaseModel

from usersetting.schema import UserSession


class JobBase(BaseModel):
    userguid: Union[str, None] = None


class JobSearchCreate(BaseModel):
    """obSearch相关接口的请求体入参"""
    cpage: Optional[int] = 1
    pagesize: Optional[int] = 10
    name: Optional[str] = None
    startdate: Optional[date] = None
    enddate: Optional[date] = None
    mguid: Optional[str] = None


class JobSearchSession(JobSearchCreate):
    """包含当前用户信息的接口入参"""
    user: Optional[UserSession] = None


class JobSearchBase(JobBase):
    """JobSearch对应的pydantic模型"""
    search_name: Union[str, None] = None
    starttime: Optional[datetime] = None
    endtime: Optional[datetime] = None
    isfinish: Union[bool, None] = None
    rowguid: str

    class Config:
        orm_mode = True


class ResumeSendBasic(JobBase):
    cname: Optional[str] = None
    mguid: str
    salary: Optional[float] = None
    heartlevel: Optional[str] = 3
    cwebsite: Optional[str] = None
    jobdescription: Optional[str] = None
    jobname: Optional[str] = None
    requirement: Optional[str] = None
    comment: Optional[str] = None
    guid: Optional[str] = None


class ResumeSendCreate(ResumeSendBasic):
    """投递记录入参对象"""
    cpage: Optional[int] = 1
    pagesize: Optional[int] = 10
    staredate: Optional[datetime] = None
    enddate: Optional[datetime] = None


class ResumeSendSession(ResumeSendCreate):
    """有用户信息的接口入参"""
    user: Optional[UserSession] = None


class ResumeSendBase(ResumeSendBasic):
    """投递记录的表实体对应"""
    rowguid: str
    sendtime: Optional[datetime] = None

    class Config:
        orm_mode = True
