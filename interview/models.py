"""面经相关的数据库模型"""
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, Float, Text, ForeignKey, Column, text, UUID, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dao.database import Base


class InterviewQuestion(Base):
    __tablename__ = 'dml_interview_question'
    rowguid: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    userguid: Mapped[str] = mapped_column(String(50))
    create_time: Mapped[datetime] = mapped_column(default=datetime.now)
    tag_name: Mapped[str] = mapped_column(String(50))
    tag_value: Mapped[str] = mapped_column(String(50))
    question: Mapped[str] = mapped_column(String(200))
    view_times: Mapped[int] = mapped_column(Integer, default=0)
    proficiency: Mapped[int] = mapped_column(Integer, default=0)
    isdel: Mapped[bool] = mapped_column(Boolean, default=False)
    answer: Mapped['InterviewAnswer'] = relationship(back_populates="question")


class InterviewAnswer(Base):
    __tablename__ = 'dml_interview_answer'
    rowguid: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    question_guid: Mapped[UUID] = mapped_column(ForeignKey("dml_interview_question.rowguid"))
    answer_content: Mapped[str] = mapped_column(Text)
    question: Mapped["InterviewQuestion"] = relationship(back_populates="answer")
