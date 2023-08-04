"""JSON Web Tokens工具类"""
import time
from datetime import datetime, timedelta

import jwt

SECRET_KEY = "your_secret_key"


def encrypt_and_expire(data: str, secret_key: str, expire_duration: int = 60):
    """加密jwt方法；expire_duration令牌有效期，默认60min"""
    # 计算过期时间
    expire_duration = timedelta(minutes=expire_duration)
    expire_time = datetime.now() + expire_duration
    # print('expire_time', expire_time.timestamp())
    # 创建JWT payload
    payload = {
        'data': data,
        'exp': expire_time
    }
    # 生成JWT令牌
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def decrypt_and_check_expiration(token, secret_key):
    """解密jwt方法"""
    try:
        payload = decrypt_token(token, secret_key)
        if type(payload) == str:
            # 说明解密出现异常返回字符串
            return payload
        # 获取数据和过期时间
        data = payload['data']
        expire_time = payload['exp']
        # 检查过期时间是否已过期;使用时间戳进行比较，避免时区导致的问题，datetime.fromtimestamp的结果默认使用UTC时区
        # if datetime.now() <= (expire_time):
        if int(time.time()) <= expire_time:
            return data
        else:
            return '令牌已失效'

    except Exception as e:
        print(e)
        return 'token解析异常'


def decrypt_token(token: str, secret_key: str):
    """解密jwt方法"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload

    except jwt.ExpiredSignatureError:
        return '令牌已过期'  # JWT令牌已过期
    except jwt.InvalidTokenError:
        return '令牌无效'  # JWT令牌无效
