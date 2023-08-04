"""登录，注册相关的数据库操作"""
from datetime import datetime

from sqlalchemy import select, text, update
from sqlalchemy.orm import Session
from uuid import uuid4

from usersetting.models import User
from usersetting.schema import UserCreate


def user_register(user: UserCreate, session: Session):
    """用户注册"""
    res = {'result': False, 'user': None}
    if not check_user_emial(user.useremail, session):
        return res
    # 暂时不使用邮箱认证
    user = User(**user.model_dump(), rowguid=str(uuid4()), created_time=datetime.now())

    session.add(user)
    session.commit()
    session.flush()
    res['user'] = user
    res['result'] = True
    return res


def check_user_emial(email: str, session: Session):
    # select(User).where(User.useremail==emial).scalar()
    stmt = text('select count(*) from dml_user WHERE  useremail=:email')
    result = session.execute(stmt, {'email': email}).scalar()

    return result == 0


def user_active(guid: str, session: Session):
    user = get_user_guid(guid, session)
    if user is None:
        return '用户不存在！'
    updatesql = update(User).where(User.rowguid == guid).values(isenable=True)
    session.execute(updatesql)
    session.commit()
    return "用户激活成功！"


def get_user_guid(guid: str, session: Session) -> User:
    return session.execute(select(User).where(User.rowguid == guid)).scalar()


def get_user_one_field(key: str, value: str, session: Session) -> User:
    stmt = select(User).where(User[key] == value)
    return session.execute(stmt).scalar()
