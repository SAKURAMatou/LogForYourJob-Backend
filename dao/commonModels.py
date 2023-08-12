"""
一些数据库通用的
"""
from datetime import datetime

from sqlalchemy import String, Text, Column, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dao.database import Base


class AttachmentFile(Base):
    __tablename__ = "dml_attachment_file"
    rowguid: Mapped[str] = mapped_column(String(50), primary_key=True)
    upload_userguid: Mapped[str] = mapped_column(String(50))  # 附件上传人
    upload_time: Mapped[datetime] = mapped_column(default=datetime.now)
    file_storages = relationship('FileStorage', back_populates='attachment')


class FileStorage(Base):
    __tablename__ = "dml_file_storage"
    rowguid: Mapped[str] = mapped_column(String(50), primary_key=True)
    storage_name: Mapped[str] = mapped_column(String(50))  # 系统保存的文件名称uuid表示
    type: Mapped[str] = mapped_column(String(10))  # 文件类型，名称的后缀
    file_name: Mapped[str] = mapped_column(Text)  # 文件name
    file_size: Mapped[float] = mapped_column(Float())  # 文件大小，单位字节
    storage_path: Mapped[str] = mapped_column(String(200))  # 存储路径
    attachment_guid = Column(String(50), ForeignKey("dml_attachment_file.rowguid"))  # 文件关联的附件guid
    attachment = relationship('AttachmentFile', back_populates='file_storages')
