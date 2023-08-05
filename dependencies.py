from fastapi import Header, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from config import get_settings
from dao.database import get_session

from login.loginCurd import get_user_guid
from utils.JWTUtil import decrypt_and_check_expiration
from usersetting.schema import UserSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="rest/token")


async def get_user_guid_token(token: str = Depends(oauth2_scheme)):
    """从请求头的token中解析用户guid"""
    settings = get_settings()
    # 根据token解密出用户guid
    userguid = decrypt_and_check_expiration(token, settings.secret_key)
    if '令牌已失效' == userguid or 'token解析异常' == userguid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userguid)
    return userguid


async def get_user_session(userguid: str = Depends(get_user_guid_token), session=Depends(get_session)) -> UserSession:
    """获取用户session信息从token中"""
    user = get_user_guid(userguid, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserSession(rowguid=user.rowguid, useremail=user.useremail, username=user.username, avatarurl=user.avatarurl,
                       isenable=user.isenable, phone=user.phone)


async def get_user_token(userguid: str = Depends(get_user_guid_token), session=Depends(get_session)):
    """获取用户从token中"""
    user = get_user_guid(userguid, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
