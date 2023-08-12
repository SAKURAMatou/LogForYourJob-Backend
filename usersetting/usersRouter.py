"""
用户设置相关接口
"""

import os
from fastapi import APIRouter, Depends, Body, UploadFile, File

from dao.database import get_session
from dependencies import get_user_token
from usersetting.models import User
from usersetting.schema import UserCreate, UserBase, UserBasicInfoEdit
from utils.requestUtil import response
from utils.JWTUtil import hash_pwd
from logger.projectLogger import logger
from dao.commonModels import AttachmentFile, FileStorage

router = APIRouter(prefix='/usersetting')


@router.get('/detail')
async def get_user_details(user: UserBase = Depends(get_user_token)):
    return response.success('用户获取成功！', {'userinfo': user})


@logger.catch
@router.post('/change/userBaseInfo')
async def edit_user_basic_info(edit_user: UserBasicInfoEdit, user: User = Depends(get_user_token),
                               session=Depends(get_session)):
    try:
        """用户基本信息修改：名称，邮箱，头像"""
        if edit_user.name is not None:
            user.username = edit_user.name
        if edit_user.email is not None:
            user.useremail = edit_user.email
        if edit_user.avatarguid is not None:
            # 根据头像的guid找到对应的头像附件对象，并获取url
            pass
        session.commit()
        return return_user_info(user, '用户基本信息修改成功！')
    except Exception as e:
        session.rollback()
        return response.fail(535, '用户基本信息修改异常！')


@logger.catch
@router.post('/change/password')
async def edit_user_pwd(newpwd: str = Body(), user: User = Depends(get_user_token), session=Depends(get_session)):
    """用户密码修改"""
    try:
        user.pwd = hash_pwd(newpwd)
        session.commit()
        return return_user_info(user, '密码修改成功！')
    except Exception as e:
        session.rollback()
        return response.fail(535, '密码修改异常！')


@logger.catch
@router.post('/change/phone')
async def gdeit_user_phone(newphone: str = Body(), user: User = Depends(get_user_token), session=Depends(get_session)):
    """用户手机号修改"""
    try:
        user.phone = newphone
        session.commit()
        return return_user_info(user, '手机号修改成功！')
    except Exception as e:
        session.rollback()
        return response.fail(535, '手机号修改异常！')


async def return_user_info(user: User, msg: str):
    return response.success(msg, {
        'userinfo': {'useremail': user.useremail, 'username': user.username, 'phone': user.phone,
                     'avatarurl': user.avatarurl}})


# 指定非必填 file: Union[UploadFile, None] = None或file: UploadFile = File(default=None)
@router.post('/change/avatar')
async def upload_avatar(file: UploadFile = File(description="upload avatar file")):
    if file:
        return {"filename": file.filename}
    else:
        return {"username": 'test'}
    pass
