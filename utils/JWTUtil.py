"""JSON Web Tokens工具类"""
import base64
import time
import bcrypt
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


def hash_pwd(pwd: str) -> str:
    """对明文密码进行加密，并通过base64转化为字符串"""
    plain_password = pwd.encode('utf-8')
    hashed_password = bcrypt.hashpw(plain_password, bcrypt.gensalt())
    # b64encode编码的结果是byte类型需要再转化为str
    # baseed =

    return base64.b64encode(hashed_password).decode('utf-8')


def check_password(input, hashed_password):
    """比较密码是否相同；bcrypt对密码进行加密的话，同一个密码加密得到的字符串也不相同，但bcrypt.checkpw比较明文和密文结果是true"""
    hashed_password_bytes = base64.b64decode(hashed_password.encode('utf-8'))
    input = input.encode('utf-8')
    return bcrypt.checkpw(input, hashed_password_bytes)
