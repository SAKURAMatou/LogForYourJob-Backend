"""logforjob的pydantic模型"""
from datetime import datetime, date
from typing import Optional, Union
from pydantic import BaseModel, validator, field_validator

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


class JobSearchResponse(BaseModel):
    guid: Optional[str] = None
    name: Optional[str] = None
    startdate: Optional[str] = None
    enddate: Optional[str] = None
    isend: Optional[str] = None


class ResumeSendBasic(JobBase):
    cname: Optional[str] = None
    mguid: Optional[str] = None
    salaryup: Optional[float] = None
    salarydown: Optional[float] = None
    heartlevel: Optional[str] = None
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
    startdate: Optional[datetime] = None
    enddate: Optional[datetime] = None
    salaryup: Optional[float] = None
    salarydown: Optional[float] = None

    @field_validator("startdate", 'enddate', 'heartlevel', mode='before')
    def empty_str_to_none(cls, v):
        return None if v == "" else v

    @field_validator('salaryup', 'salarydown', mode='before')
    def int_zero_to_none(cls, v):
        return None if v == 0 else v


class ResumeSendSession(ResumeSendCreate):
    """有用户信息的接口入参"""
    user: Optional[UserSession] = None


class ResumeSendBase(ResumeSendBasic):
    """投递记录的表实体对应"""
    rowguid: str
    sendtime: Optional[datetime] = None

    class Config:
        orm_mode = True


class ResumeSendResponse(BaseModel):
    guid: Optional[str] = None
    cname: Optional[str] = None
    jobname: Optional[str] = None
    salaryup: Union[str, float] = None
    salarydown: Union[str, float] = None
    salary: Union[str, None] = None
    sendtime: Union[str, datetime] = None
    requirement: Optional[str] = None
    heartlevel: Optional[str] = None
    jobdescription: Optional[str] = None
    comment: Optional[str] = None
    mguid: Optional[str] = None
    mname: Optional[str] = None
    cwebsite: Optional[str] = None
