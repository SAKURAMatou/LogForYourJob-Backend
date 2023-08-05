from datetime import datetime

from sqlalchemy import String, Boolean, Float, Text, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column

from dao.database import Base


class JobSearch(Base):
    __tablename__ = 'dml_job_search'
    rowguid: Mapped[str] = mapped_column(String(50), primary_key=True)
    search_name: Mapped[str] = mapped_column(String(20))
    starttime: Mapped[datetime] = mapped_column(default=datetime.now)
    endtime: Mapped[datetime] = mapped_column(default=None)
    isfinish: Mapped[bool] = mapped_column(Boolean, default=False)
    userguid: Mapped[str] = mapped_column(String(50))


class ResumeSend(Base):
    __tablename__ = 'dml_resume_send'
    rowguid: Mapped[str] = mapped_column(String(50), primary_key=True)
    # mguid: Mapped[str] = mapped_column(String(50))
    cname: Mapped[str] = mapped_column(String(20))
    jobname: Mapped[str] = mapped_column(String(20))
    salary: Mapped[float] = mapped_column(Float(precision=1))
    sendtime: Mapped[datetime] = mapped_column(default=datetime.now)
    cwebsite: Mapped[str] = mapped_column(String(100), default=None)
    heartlevel: Mapped[str] = mapped_column(String(1), default='3')
    jobdescription: Mapped[str] = mapped_column(Text, default=None)
    requirement: Mapped[str] = mapped_column(Text, default=None)
    comment: Mapped[str] = mapped_column(Text, default=None)
    mguid = Column(String(50), ForeignKey("dml_job_search.rowguid"))
    userguid: Mapped[str] = mapped_column(String(50))
