from fastapi import APIRouter, Depends, Response

from dao.database import get_session
from dependencies import get_user_token
from usersetting.models import User
from usersetting.schema import UserCreate, UserLogin
from .loginCurd import user_register, user_active, get_user_one_field
from utils.requestUtil import response
from config import get_settings
from utils.JWTUtil import encrypt_and_expire, decrypt_and_check_expiration, hash_pwd, check_password

router = APIRouter(prefix="/user")


@router.post("/register")
async def register(userCreate: UserCreate, session=Depends(get_session)):
    """用户注册"""
    userCreate.pwd = hash_pwd(userCreate.pwd)

    res = user_register(userCreate, session)
    if not res['result']:
        return response.fail(521, "用户已存在", {'useremail': userCreate.useremail, 'username': userCreate.username})
    #   TODO 发送用户激活邮件，邮件中添加一段html点击html中的连接调用激活接口（get请求）激活用户
    send_activity_email(res['user'])
    return response.success("注册成功", {'useremail': userCreate.useremail, 'username': userCreate.username})


@router.post("/login")
async def login(userLogin: UserLogin, requestResponse: Response, session=Depends(get_session)):
    """用户登录"""
    users = get_user_one_field('useremail', userLogin.name, session)
    if not users:
        users = get_user_one_field('phone', userLogin.name, session)

    if users is None:
        return response.fail(521, "用户不存在")
    user = users[0]
    settings = get_settings()
    token = ''
    # 比较密码是否相同,
    if not check_password(userLogin.pwd, user.pwd):
        return response.fail(531, "用户名或密码错误！")
    if not user.isenable:
        return response.fail(532, "用户已被禁用，或尚未激活！")
    # 密码相同则登录成功，生成token
    token = encrypt_and_expire(user.rowguid, settings.secret_key)
    # 拼接用户头像的访问地址:host/url
    avatarurl = ''
    if user.avatarurl is not None:
        base_url = user.avatarurl.strip("/")
        host = settings.system_host.strip("/")
        avatarurl = f'{host}/{base_url}'

    requestResponse.set_cookie(key='token', value=token,
                               httponly=True, max_age=settings.token_expires_in * 60)
    return response.success("登录成功", {'token': token, 'avatarurl': avatarurl, 'useremail': user.useremail,
                                     'username': user.username})


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


@router.post("/logout", dependencies=Depends(get_user_token))
async def log_out(requestResponse: Response):
    requestResponse.set_cookie(key="token", value="", max_age=0)
    return response.success("登出成功！")
