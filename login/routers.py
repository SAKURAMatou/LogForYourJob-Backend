from fastapi import APIRouter, Depends
import bcrypt

from dao.database import get_session
from usersetting.schema import UserCreate
from .loginCurd import user_register, user_active
from utils.requestUtil import response
from config import get_settings
from utils.JWTUtil import encrypt_and_expire, decrypt_and_check_expiration

router = APIRouter(prefix="/user")


@router.post("/register")
async def register(userCreate: UserCreate, session=Depends(get_session)):
    """用户注册"""
    plain_password = userCreate.pwd.encode('utf-8')
    hashed_password = bcrypt.hashpw(plain_password, bcrypt.gensalt())
    userCreate.pwd = hashed_password

    res = user_register(userCreate, session)
    if not res['result']:
        return response.fail(521, "用户已存在", {'useremail': userCreate.useremail, 'username': userCreate.username})
    #   TODO 发送用户激活邮件，邮件中添加一段html点击html中的连接调用激活接口（get请求）激活用户
    send_activity_email(res['user'])
    return response.success("注册成功", {'useremail': userCreate.useremail, 'username': userCreate.username})


@router.post("/login")
async def login():
    """用户登录"""
    pass


@router.get("/activate/{token}")
async def user_activate(token: str, session=Depends(get_session)):
    """激活用户"""
    settings = get_settings()
    userguid = decrypt_and_check_expiration(token, settings.activity_key)
    res = user_active(userguid, session)
    return res


def send_activity_email(user):
    """发送账号激活邮件"""
    setting = get_settings()
    token = encrypt_and_expire(user.rowguid, setting.activity_key, 10)
    activity_url = f'{setting.system_host}/user/activate/{token}'
    print(activity_url)
    # TODO 邮件发送操作
