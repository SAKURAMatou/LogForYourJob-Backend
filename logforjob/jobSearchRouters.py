from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dao.database import get_session
from dependencies import get_user_session
from logforjob.schema import JobSearchCreate, JobSearchSession, ResumeSendCreate, ResumeSendSession
from usersetting.schema import UserSession
from utils.requestUtil import response
from .jobCurd import add_job_search


async def set_userguid_jobsearch(jobSearchCreate: JobSearchCreate, user: UserSession = Depends(get_user_session)):
    return JobSearchSession(**jobSearchCreate.model_dump(), user=user)


async def set_user_resume(uesumeSendCreate: ResumeSendCreate, user: UserSession = Depends(get_user_session)):
    return ResumeSendSession(**uesumeSendCreate.model_dump(), user=user)


router = APIRouter(prefix='/logforyourjobs')


@router.post("/getmainlist")
async def getmainlist(jobSearchCreate: JobSearchSession = Depends(set_userguid_jobsearch),
                      session=Depends(get_session)):
    """获取求职经历列表"""
    print(jobSearchCreate)
    pass


@router.post("/addJobSearchLog")
async def addJobSearchLog(jobSearchSession: JobSearchSession = Depends(set_userguid_jobsearch),
                          session: Session = Depends(get_session)):
    """添加求职经历"""
    if not jobSearchSession.mname:
        return response.fail(531, "求职经历名称必填！")
    if not jobSearchSession.startdate:
        return response.fail(531, "开始时间必填！")

    try:
        add_job_search(jobSearchSession, session)
        return response.success("添加成功")
    except Exception as e:
        print(e)
        session.rollback()
        return response.fail(550, "出现异常！")
