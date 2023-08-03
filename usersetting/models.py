from datetime import datetime


from sqlalchemy import String, Text, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass

from dao.database import Base


class User(Base):
    """sqlalchemy的dml_usermodel"""
    __tablename__ = "dml_user"
    rowguid: Mapped[str] = mapped_column(String(50), primary_key=True)
    pwd: Mapped[str] = mapped_column(Text)
    avatarurl: Mapped[str] = mapped_column(Text)
    useremail: Mapped[str] = mapped_column(String(50))
    username: Mapped[str] = mapped_column(String(50))
    created_time: Mapped[datetime] = mapped_column(
        default=None
    )
    phone: Mapped[str] = mapped_column(String(20))
    isenable: Mapped[bool] = mapped_column(Boolean, default=False)
