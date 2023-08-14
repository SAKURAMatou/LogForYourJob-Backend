from fastapi import APIRouter, Depends, Response, HTTPException

from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from dao.database import get_session
from dependencies import get_user_token
from usersetting.schema import UserCreate, UserLogin
from utils.emailUtil import send_email
from .loginCurd import user_register, user_active, get_user_one_field
from utils.requestUtil import response
from config import get_settings, Settings
from utils.JWTUtil import encrypt_and_expire, decrypt_and_check_expiration, hash_pwd, check_password
from logger.projectLogger import logger

router = APIRouter(prefix="/user")


@router.post("/register")
async def register(userCreate: UserCreate, session: Session = Depends(get_session)):
    """用户注册"""
    try:
        userCreate.pwd = hash_pwd(userCreate.pwd)
        res = user_register(userCreate, session)
        if not res['result']:
            return response.fail(521, "用户已存在", {'useremail': userCreate.useremail, 'username': userCreate.username})

        setting = get_settings()
        user = res['user']
        token = encrypt_and_expire(user.rowguid, setting.activity_key, 10)
        activity_url = f'{setting.system_host}/user/activate/{token}'

        send_email(get_sctivity_email_content(activity_url), "LogForYouJob 账号激活",
                   f'LogForYouJob<{setting.smtp_username}>',
                   user.useremail, subtype='html')

        session.commit()
        session.flush()
        return response.success(f'用户{userCreate.username}注册成功，请前往邮箱{userCreate.useremail}查看激活邮件进行用户激活！',
                                {'useremail': userCreate.useremail, 'username': userCreate.username})
    except Exception as e:
        logger.exception(e)
        session.rollback()
        return response.fail(522, "注册出现异常！")


@router.post("/login")
async def login(userLogin: UserLogin, requestResponse: Response, session: Session = Depends(get_session)):
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
async def user_activate(token: str, session: Session = Depends(get_session)):
    """激活用户"""
    try:
        settings = get_settings()
        userguid = decrypt_and_check_expiration(token, settings.activity_key)
        res = user_active(userguid, session)
        session.commit()
        return RedirectResponse(settings.fornt_host)
    except Exception as e:
        logger.exception(e)
        session.rollback()
        return response.fail(523, "用户激活出现异常！")


def get_sctivity_email_content(activity_url: str):
    return f"""<div class="active-container" style=" display: flex; justify-content: center;  align-items: center;">
    <div class="active-show" style="width: 360px;height: 360px;vertical-align: middle;">
        <div>
            <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjc0IiBoZWlnaHQ9Ijc0IiB2aWV3Qm94PSIwIDAgMjc0IDc0IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIj4KPGcgc3R5bGU9Im1peC1ibGVuZC1tb2RlOm11bHRpcGx5Ij4KPHJlY3Qgd2lkdGg9IjI3NCIgaGVpZ2h0PSI3NCIgZmlsbD0idXJsKCNwYXR0ZXJuMCkiLz4KPC9nPgo8ZGVmcz4KPHBhdHRlcm4gaWQ9InBhdHRlcm4wIiBwYXR0ZXJuQ29udGVudFVuaXRzPSJvYmplY3RCb3VuZGluZ0JveCIgd2lkdGg9IjEiIGhlaWdodD0iMSI+Cjx1c2UgeGxpbms6aHJlZj0iI2ltYWdlMF81XzEzNjgiIHRyYW5zZm9ybT0ic2NhbGUoMC4wMDM2NDk2NCAwLjAxMzUxMzUpIi8+CjwvcGF0dGVybj4KPGltYWdlIGlkPSJpbWFnZTBfNV8xMzY4IiB3aWR0aD0iMjc0IiBoZWlnaHQ9Ijc0IiB4bGluazpocmVmPSJkYXRhOmltYWdlL3BuZztiYXNlNjQsaVZCT1J3MEtHZ29BQUFBTlNVaEVVZ0FBQVJJQUFBQktDQUlBQUFENC8weGFBQUFBQ1hCSVdYTUFBQTdFQUFBT3hBR1ZLdzRiQUFBQUVYUkZXSFJUYjJaMGQyRnlaUUJUYm1sd1lYTjBaVjBYenQwQUFBa1JTVVJCVkhpYzdkMS9hQk5wR2dmdzc4d2treWEyUzZHd1J3S0Y5Qjk3QlN1bHJRb3RDK3N0V0sycDNiMjFMbXV0ZDJ2dHVvV1RWamlSZzdZczltNFhPVUZGYUhHOXJyZGJLOWhhcnRXNi9nRFA1VTRyUml1RkNyc3RCeTBJQ1NkWEVLSkpNOGxNN28rMHBrbWJtbmN5azhUczg2Ri8yR1FtNytOMG5ubC96b1FMaFVJZ2hMRGcweDBBSVc4ZlNodENtRkhhRU1LTTBvWVFacFEyaERDanRDR0VHYVVOSWN3b2JRaGhSbWxEQ0ROS0cwS1lVZG9Rd3N5UTdnRGVJSER0aUwvN1BsQXRqSjB5djV2dWFKWXNSUlZQbzlIWlprcGRPQUNBeVRNdlB4K0kvRnJWWVRxOXl4anpZbG9DaTBQVHYreVVkM096QXFDcEwvZHdxUmJSdlFIVk5vUXd5L1RhSnJObFVoMVkxcGI3WUx2M3QwMktHOWh3VkR5OXl3aWdyTTN5M1R2ZTMvVUN3TEdSM0k5dGFRNHlXMUJ0azBXRVlzUCtVZ0I0T2hEOEtmeVNKRjN2QXdCemcyRUg1WXhtS0cyeWlyampBRzhHNEZMR3B4VUFudnZ5b0FRQSszZUpsdlNHbGxXeXRwRVdlRGdVR0w2cVBKeUdEOGkzYzFWYitVLzJtVXJ5NGw0bjVQbUZTNmZseTNkRHp5WGsyN202WmtPTlA3anZ6eUdBNjd5eHJxNGd4Vkg1ejI0TzlDLzd2YWt2OTNDcDh2enhRcyszeXZoanZBRE1CZGpiYlQ1VUtTemZ6Vkl0N0xjcDUxejQvcXJVZEZRWXZ4a0NnRkpoVy9FYUYwaVdZeFduOC8zODZpdEgybzVWaFB3LzZkOFhBdWNHUXpQek1CZGd5M2JoNEFIVCtqVjNVU1ViMDBaMitUcWE1RHVleUNzdjVrSS9YSkIvR1BEdVBXRTZYRzBVVnV6aW5mSiszcXJNU0pIdCt6dWp6dHEwUkJVdE9IbG1ZZm13bU0vRWI5bTRjaWZUdHNiQXViL0NOeVRmM1I2NmZCY0E5clNLaFhwRnBRdlZVVjA2SmwxYStyZHZIajhPeUQ5ZTlYM1piNjYxYVpzNTJkZElreFpPN3BIdmVJQTg3bENQNlo0ejErbTAzTDRzN0MwR0pGdzY0dStmVm1KMzhmaStDdWVNbmV2c056MXc1anFkT2NOOS9BZDVhWXpLZE5pWjYzVG1PdnNXLzBMZW0xTGJFTmQ4U3J4eHorSjA1ajY0Wnhyc01aYUpxeFJWV0cvWUl3SUk5WFRLVHdIWStKMlZjVTR6RmNjcUJaS0l5bHpLbngzSmVlRE1kVHBOZzkyOEhZQW45R1duZjA3akVMTXRiWlNmQm9MREVnRDg4Vy9tNWtxakNBQjhmcEc1dmMrdzF3WUFQZC82WDBUdk0zTkZ2aDNlNVlTNXJqaDhKVE1VbGxxT3RIRnZLTzIrN05qOGNuUFVqM2RTbzZoaURBK0ZqZ3lhRDFXTEJTSVBRQkNOZHB0eDlVMUZjV2N6QUxoZEFGQjF3Rml5K25ZYVJLV0RwS0xhM1c3WllqTUlBR0MwMStTYzZlRE1BS2JrSzQ5bFRZUE10clFKUEJ3RkFHd1Z0aFZGLzkvRW5BOGJBUUIzbGZINTVXOUlrLzhFQU5RSU80cDBPaHdxb29wbGJqVFVKZHJTNEV0cWhBMkxuODkvdWoxT2Rta1JsUTQwaklxMzdqTHNGZ0hnMnFPZ3BrRm1YZC9HNHdLQWtrb2hmOFZiOWwvemdBS0Vucm1BU0xjMTlOOXBBQ2paS0RBM3loS2V0MkdQS2xadHBZR2htMkV6ZkZRdFA3MFBiT0tLVm12SWFSV1ZIalNOaXJkdkF1N0RONk04QjdTYllkUGw4cXE0M2I3V1ZsOXJxK0oyNi9INWF3aUZLMk9MNlUzdHF4VmV2TlR2eVZmcW8zck44bzdtblhNTm9rcVlrbkFqS1pWUnFhWkwyc2dURTY5LzlQajhOWEQ1TmdDWWVCVDBySGh2N3Vkd1Y1SXJqSnI0NDM1VkRBRHVueFhkMnZFcW9rb0JEYU9TL3pNZDU2TGo4Vi9yZlhYZ0ErK0lLK1lOWlg0V0FNenIrZWhLUU50anBjdzlXcldVSkdWYjM4YTRwUjRBY0V1K01SczkzaUl0aklSSGI3ZnlWVkgxdTFqMkd3REFYZm4yckU0RFJ5cWlTZ0dWVVprQkFMSS9zb3Zza2dhSDRwV2lqRjhJUGZYZys2RUY3N0pYNVZubFh5NEFxTjBZMDAvUThsZzl2eFc4SWdGQTNTWnRleVBabGpaOFNhUGhZeEVBVGg3MDlVOEZKQUJRdks2RmM2M0JTeTRBYU40bnhqU2ExKzhXdGkzdE1qd2QzaVg0N0xHMys0eFd6VFkxVWVsUFZWVEZmQzBBNEI4RC9qbEpBUlR2ck8rcmR0bThOVTZiS2svOHBCRUEzQVBCOXQ0RnQ2UUFpdVJhT0hWc2NYQzhabE5NNHpPcFkzWGx0UGVoS3lnRFFHRHVsdmNQblNFZmdGSmhkN3doZUpVNFBSNW1HeGdiOHg4L0RzRFUxV1YwT0pMNktCVkw5RmRPbGkwU2tlQjBaN1NWTTk5cUZyMHpSaFc3U21BSi80M1RVaGEvbEtYWitsanhWdFN6SHl0bDVvSjNYMi9VUy9aRzQ5ZEZ3VS9qclJLUS9IOXZEZlJNclZKRWMyL09vZEpWNmdIbXFKYldMcXdpajh1YzZVNTVZaUl3TnBaNGoxOXh1NW0yVDRwZ00zOTl4L1JOQi85KzhXS0xJdC9PMVg0bVhMeGhhWTh6d1d3cHRYdzNhanpXd0wwckxtN2YxRzI4MktGbHIxUkZWQ25BSGhXLy9yT2NpeDE4V1FFQW1BdTQycVBHdmpiVFdvT1FvdW4zZlRtRHAvamFTb1FQTC9Ld3BZWS9PMnBaTldkVVJiV29xY2QwdG8xYmlnM3Z0eG9HUnpUUEdhaXJiUlMzMjF0ZmovaVZ5Y3JhNWxWOWZjanROamdjT1YxZFNjZWNLanFzc3lMWklhazhEQ1ZjZTRTM1RIejdGRlBjMC80VkxZTGc0dWlReUJWU3pwQW8yVFlrb01xOC8yUnp3TkhrSFo2U1BKSUNRSllDa3hmOGZ4b0NnQTF0aGxUY1prdmVKbG0zU2tDRlo0K1ZLUW0rYWVWRXMzUUNVY01DOWwzQ1h4ckVkSFU4U0thaXRBRUthOWJkcUpMR2J3YXZYVlVtcC9FQ2dJajExZnhIRGNZUEs5UFdXU2NaVEp1MENZOEJpQzB0WWt1TEh0dnJUc2dUMzJzUTMydElkeHprN2FCTjN5WjQvVHFBd05oWWd0dEw1ODhEa0o4ODBhUjBRbEtNaGdRSVlVWnBRd2d6U2h0Q21DV2FOb0d4c2RUZkJVQklaa3BvSkUwNmZ6N2NpYmVNanZKV3E4NGhFWkxwRXFwdFVuK1RKaUdaalBvMmhEQ0xOTklVdHp1NHRMYWZ0MXBUUEJHNXZIUkM5SmJrR1I1Skc5OFhYeXhmb1N5VWx3c1ZGVW1GeHNKLy9EZ05PWkJVU3VZTWp6VFNlQnM5a1o3OGduQkpuUENSMnNiVTFmWDZlaTlVVktSNHhHeDU2WVRvTGNrelBKSTJ2TlhLSjNmZmZ6TFNXem9oVEdna2pSQm1DYVZOdURyanJGYWE2eVFFQ2E0U0VGdGFoUEx5WkxwUWhHU1RSRzlUUytWZ05DRVpqdm8yaERDanRDR0VHYVVOSWN5MGVRU0hlUERnZ3N1VitCTTN4WllXK2NrVDQ4NmRtcFJPU0lwcGt6WkNSY1c2MGRIRXR6YzZIRWsrVXAyUU5LSkdHaUhNS0cwSVlVWnBRd2d6TlduRFc2M2MwbktiQkhjSno1WUs1ZVVxaWlNazA2Z2NFbGczT2lwUFRDUytkTURjMjZ1NDNiU2tqV1FIOVkwMDF1VTJsRE1rYTFEZmhoQm1sRGFFTU5NM2JhaGhScktTTGw4TFpYUTR3bC9DUWJjYmtLeWs1cHVpQ2ZtRm83NE5JY3dvYlFoaFJtbERDRE5LRzBLWVVkb1F3b3pTaGhCbS93YzFRWFBTSGFLWmV3QUFBQUJKUlU1RXJrSmdnZz09Ii8+CjwvZGVmcz4KPC9zdmc+">
        </div>
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
