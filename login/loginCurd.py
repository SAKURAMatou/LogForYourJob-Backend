"""登录，注册相关的数据库操作"""
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session
from uuid import uuid4

from usersetting.models import User
from usersetting.schema import UserCreate
from utils.requestUtil import response


def user_register(user: UserCreate, session: Session):
    """用户注册"""

    if not check_user_emial(user.useremail, session):
        return response.fail(521, "用户已存在", {'useremail': user.useremail, 'username': user.username})
    user = User(**user.model_dump(), rowguid=str(uuid4()), created_time=datetime.now())

    session.add(user)
    session.commit()
    session.flush()
    return response.success("注册成功", {'useremail': user.useremail, 'username': user.username})


def check_user_emial(email: str, session: Session):
    # select(User).where(User.useremail==emial).scalar()
    stmt = text('select count(*) from dml_user WHERE  useremail=:email')
    result = session.execute(stmt, {'email': email}).scalar()

    return result == 0
