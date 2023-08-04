from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from config import get_settings
from dao.database import get_session
from .loginCurd import get_user_one_field
from utils.JWTUtil import encrypt_and_expire, hash_pwd, check_password

router = APIRouter()


@router.post("/rest/token")
async def get_token(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    users = get_user_one_field('useremail', form_data.username, session)

    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not existing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = users[0]
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # 比较密码是否相同,对入参的密码进行加密
    # hashed_password = hash_pwd(form_data.password)
    if not check_password(form_data.password, user.pwd):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    settings = get_settings()
    # 密码相同则登录成功，生成token
    token = encrypt_and_expire(user.rowguid, settings.secret_key)
    return {"access_token": token, "token_type": "bearer", 'expires_in': f'{settings.token_expires_in} min'}
