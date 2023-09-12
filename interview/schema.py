"""面经相关的pydantic模型"""
from datetime import datetime

from pydantic import BaseModel
from typing import Optional, Union


class QuestionBase(BaseModel):
    userguid: Union[str, None] = None


class InterviewBase(BaseModel):
    rowguid: str


class InterviewQuestion(InterviewBase):
    userguid: Optional[str] = None
    create_time: Optional[datetime] = None
    tag_name: Optional[str] = None
    tag_value: Optional[str] = None
    question: Optional[str] = None
    view_times: Optional[int] = 0
    proficiency: Optional[int] = 0
    isdeleted: Optional[bool] = False

    class Config:
        orm_mode = True


class InterviewAnswerView(InterviewBase):
    answer_content: Optional[str] = None
    question_guid: Optional[str] = None

    class Config:
        orm_mode = True


class QuestionGuid(BaseModel):
    pass


class QuestionAddParam(BaseModel):
    """新增问题入参对象"""
    question: str
    answer: str
    tagName: str
    tagValue: str
    view_times: Optional[int] = 0
    proficiency: Optional[int] = 0
    isdel: Optional[bool] = False


class QuestionModifyParam(InterviewBase):
    """修改问题入参"""
    answer: Optional[str] = None
    tagName: Optional[str] = None
    tagValue: Optional[str] = None


class QuestionListParam(QuestionBase):
    cpage: Optional[int] = 1
    pagesize: Optional[int] = 10
    tagvalue: Optional[str] = None
    keyword: Optional[str] = None


class Questionguid(BaseModel):
    questionguid: Optional[str] = None


class QuestionResponse(BaseModel):
    kguid: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    tagname: Optional[str] = None


class QuestionDetailResponse(BaseModel):
    rowguid: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    tagvalue: Optional[str] = None
