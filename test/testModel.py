from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AttachmentFile(Base):
    __tablename__ = "dml_attachment_file"
    rowguid: Mapped[str] = mapped_column(String(50), primary_key=True)
    upload_userguid: Mapped[str] = mapped_column(String(50))  # 附件上传人
    upload_time: Mapped[datetime] = mapped_column(default=datetime.now())
