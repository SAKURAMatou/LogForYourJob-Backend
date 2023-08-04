from fastapi import Header, HTTPException, Depends, status

from config import get_settings
from dao.database import get_session
from main import oauth2_scheme
from login.loginCurd import get_user_guid
from utils.JWTUtil import decrypt_and_check_expiration, hash_pwd


async def get_user_guid_token(token: str = Depends(oauth2_scheme)):
    """从请求头的token中解析用户guid"""
    settings = get_settings()
    # 根据token解密出用户guid
    userguid = decrypt_and_check_expiration(token, settings.secret_key)
    if '令牌已失效' == userguid or 'token解析异常' == userguid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=userguid)
    return userguid


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
