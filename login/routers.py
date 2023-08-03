from fastapi import APIRouter, Depends
import bcrypt

from dao.database import get_session
from usersetting.schema import UserCreate
from .loginCurd import user_register

router = APIRouter(prefix="/user")


@router.post("/register")
async def register(userCreate: UserCreate, session=Depends(get_session)):
    """用户注册"""
    plain_password = userCreate.pwd.encode('utf-8')
    hashed_password = bcrypt.hashpw(plain_password, bcrypt.gensalt())
    userCreate.pwd = hashed_password

    res = user_register(userCreate, session)
    return res


@router.post("/login")
async def login():
    """用户登录"""
    pass
