from fastapi import APIRouter, Depends, Response, HTTPException
import smtplib
from email.message import EmailMessage

from dao.database import get_session
from dependencies import get_user_token
from usersetting.schema import UserCreate, UserLogin
from .loginCurd import user_register, user_active, get_user_one_field
from utils.requestUtil import response
from config import get_settings, Settings
from utils.JWTUtil import encrypt_and_expire, decrypt_and_check_expiration, hash_pwd, check_password

router = APIRouter(prefix="/user")


@router.post("/register")
async def register(userCreate: UserCreate, session=Depends(get_session)):
    """用户注册"""
    userCreate.pwd = hash_pwd(userCreate.pwd)

    res = user_register(userCreate, session)
    if not res['result']:
        return response.fail(521, "用户已存在", {'useremail': userCreate.useremail, 'username': userCreate.username})

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

    requestResponse.set_cookie(key='token', value=f'Bearer {token}',
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
    msg = EmailMessage()
    msg.set_content(get_sctivity_email_content(activity_url), subtype='html', charset='utf-8')
    msg["Subject"] = "LogForYouJob 账号激活"
    msg["From"] = 'LogForYouJob <dmlpl456@qq.com>'
    msg["To"] = user.useremail

    try:
        with smtplib.SMTP_SSL(setting.smtp_server, setting.smtp_port) as server:
            server.login(setting.smtp_username, setting.smtp_password)
            server.send_message(msg)

        return {"message": "Activation email sent successfully!"}

    except Exception as e:
        raise HTTPException(status_code=539, detail=f"Error sending email: {e}")


def get_sctivity_email_content(activity_url: str):
    return f"""<div class="active-container" style=" display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh">
    <div class="active-show" style="width: 360px;height: 360px;vertical-align: middle;">
        <svg width="274" height="74" viewBox="0 0 274 74" fill="none" xmlns="http://www.w3.org/2000/svg"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <g style="mix-blend-mode:multiply">
                <rect width="274" height="74" fill="url(#pattern0)"/>
            </g>
            <defs>
                <pattern id="pattern0" patternContentUnits="objectBoundingBox" width="1" height="1">
                    <use xlink:href="#image0_5_1368" transform="scale(0.00364964 0.0135135)"/>
                </pattern>
                <image id="image0_5_1368" width="274" height="74"
                       xlink:href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARIAAABKCAIAAAD4/0xaAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAEXRFWHRTb2Z0d2FyZQBTbmlwYXN0ZV0Xzt0AAAkRSURBVHic7d1/aBNpGgfw78wkkya2S6GwRwKF9B97BSulrQotC+stWK2p3b21Lmutd2vtuoWTVjiRg7Ys9m4XOUFFaHG9rrdbK9hartW6/gDP5U4rRiuFCrstBy0ICSdXEKJJM8lM7o+0pkmbmncyk8Ts86F/2GQm7+N0nnl/zoQLhUIghLDg0x0AIW8fShtCmFHaEMKM0oYQZpQ2hDCjtCGEGaUNIcwobQhhRmlDCDNKG0KYUdoQwsyQ7gDeIHDtiL/7PlAtjJ0yv5vuaJYsRRVPo9HZZkpdOACAyTMvPx+I/FrVYTq9yxjzYloCi0PTv+yUd3OzAqCpL/dwqRbRvQHVNoQwy/TaJrNlUh1Y1pb7YLv3t02KG9hwVDy9ywigrM3y3Tve3/UCwLGR3I9taQ4yW1Btk0WEYsP+UgB4OhD8KfySJF3vAwBzg2EH5YxmKG2yirjjAG8G4FLGpxUAnvvyoAQA+3eJlvSGllWytpEWeDgUGL6qPJyGD8i3c1Vb+U/2mUry4l4n5PmFS6fly3dDzyXk27m6ZkONP7jvzyGA67yxrq4gxVH5z24O9C/7vakv93Cp8vzxQs+3yvhjvADMBdjbbT5UKSzfzVIt7Lcp51z4/qrUdFQYvxkCgFJhW/EaF0iWYxWn8/386itH2o5VhPw/6d8XAucGQzPzMBdgy3bh4AHT+jV3USUb00Z2+Tqa5DueyCsv5kI/XJB/GPDuPWE6XG0UVuzinfJ+3qrMSJHt+zujztq0RBUtOHlmYfmwmM/Eb9m4cifTtsbAub/CNyTf3R66fBcA9rSKhXpFpQvVUV06Jl1a+rdvHj8OyD9e9X3Zb661aZs52ddIkxZO7pHveIA87lCP6Z4z1+m03L4s7C0GJFw64u+fVmJ38fi+CueMnevsNz1w5jqdOcN9/Ad5aYzKdNiZ63TmOvsW/0Lem1LbENd8Srxxz+J05j64ZxrsMZaJqxRVWG/YIwII9XTKTwHY+J2VcU4zFccqBZKIylzKnx3JeeDMdTpNg928HYAn9GWnf07jELMtbZSfBoLDEgD88W/m5kqjCAB8fpG5vc+w1wYAPd/6X0TvM3NFvh3e5YS5rjh8JTMUllqOtHFvKO2+7Nj8cnPUj3dSo6hiDA+FjgyaD1WLBSIPQBCNdptx9U1FcWczALhdAFB1wFiy+nYaRKWDpKLa3W7ZYjMIAGC01+Sc6eDMAKbkK49lTYPMtrQJPBwFAGwVthVF/9/EnA8bAQB3lfH55W9Ik/8EANQIO4p0OhwqooplbjTUJdrS4EtqhA2Ln89/uj1OdmkRlQ40jIq37jLsFgHg2qOgpkFmXd/G4wKAkkohf8Vb9l/zgAKEnrmASLc19N9pACjZKDA3yhKet2GPKlZtpYGhm2EzfFQtP70PbOKKVmvIaRWVHjSNirdvAu7DN6M8B7SbYdPl8qq43b7WVl9rq+J26/H5awiFK2OL6U3tqxVevNTvyVfqo3rN8o7mnXMNokqYknAjKZVRqaZL2sgTE69/9Pj8NXD5NgCYeBT0rHhv7udwV5IrjJr4435VDADunxXd2vEqokoBDaOS/zMd56Lj8V/rfXXgA++IK+YNZX4WAMzr+ehKQNtjpcw9WrWUJGVb38a4pR4AcEu+MRs93iItjIRHb7fyVVH1u1j2GwDAXfn2rE4DRyqiSgGVUZkBALI/sovskgaH4pWijF8IPfXg+6EF77JX5VnlXy4AqN0Y00/Q8lg9vxW8IgFA3SZteyPZljZ8SaPhYxEATh709U8FJABQvK6Fc63BSy4AaN4nxjSa1+8Wti3tMjwd3iX47LG3+4xWzTY1UelPVVTFfC0A4B8D/jlJARTvrO+rdtm8NU6bKk/8pBEA3APB9t4Ft6QAiuRaOHVscXC8ZlNM4zOpY3XltPehKygDQGDulvcPnSEfgFJhd7wheJU4PR5mGxgb8x8/DsDU1WV0OJL6KBVL9FdOli0SkeB0Z7SVM99qFr0zRhW7SmAJ/43TUha/lKXZ+ljxVtSzHytl5oJ3X2/US/ZG49dFwU/jrRKQ/H9vDfRMrVJEc2/OodJV6gHmqJbWLqwij8uc6U55YiIwNpZ4j19xu5m2T4pgM399x/RNB/9+8WKLIt/O1X4mXLxhaY8zwWwptXw3ajzWwL0rLm7f1G282KFlr1RFVCnAHhW//rOcix18WQEAmAu42qPGvjbTWoOQoun3fTmDp/jaSoQPL/KwpYY/O2pZNWdURbWoqcd0to1big3vtxoGRzTPGairbRS321tfj/iVycra5lV9fcjtNjgcOV1dScecKjqssyLZIak8DCVce4S3THz7FFPc0/4VLYLg4uiQyBVSzpAo2TYkoMq8/2RzwNHkHZ6SPJICQJYCkxf8fxoCgA1thlTcZkveJlm3SkCFZ4+VKQm+aeVEs3QCUcMC9l3CXxrEdHU8SKaitAEKa9bdqJLGbwavXVUmp/ECgIj11fxHDcYPK9PWWScZTJu0CY8BiC0tYkuLHtvrTsgT32sQ32tIdxzk7aBN3yZ4/TqAwNhYgttL588DkJ880aR0QlKMhgQIYUZpQwgzShtCmCWaNoGxsdTfBUBIZkpoJE06fz7cibeMjvJWq84hEZLpEqptUn+TJiGZjPo2hDCLNNIUtzu4tLaft1pTPBG5vHRC9JbkGR5JG98XXyxfoSyUlwsVFUmFxsJ//DgNOZBUSuYMjzTSeBs9kZ78gnBJnPCR2sbU1fX6ei9UVKR4xGx56YToLckzPJI2vNXKJ3fffzLSWzohTGgkjRBmCaVNuDrjrFaa6yQECa4SEFtahPLyZLpQhGSTRG9TS+VgNCEZjvo2hDCjtCGEGaUNIcy0eQSHePDggsuV+BM3xZYW+ckT486dmpROSIppkzZCRcW60dHEtzc6HEk+Up2QNKJGGiHMKG0IYUZpQwgzNWnDW63c0nKbBHcJz5YK5eUqiiMk06gcElg3OipPTCS+dMDc26u43bSkjWQH9Y001uU2lDMka1DfhhBmlDaEMNM3bahhRrKSLl8LZXQ4wl/CQbcbkKyk5puiCfmFo74NIcwobQhhRmlDCDNKG0KYUdoQwozShhBm/wc1QXPSHaKZewAAAABJRU5ErkJggg=="/>
            </defs>
        </svg>
        <h1>
            欢迎注册
        </h1>
        <a href="{activity_url}" target="_blank">点击激活账号</a>
    </div>
</div>"""


@router.post("/logout", dependencies=[Depends(get_user_token)])
async def log_out(requestResponse: Response):
    requestResponse.set_cookie(key="token", value="", max_age=0)
    return response.success("登出成功！")
