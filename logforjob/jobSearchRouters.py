from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dao.database import get_session
from dependencies import get_user_session
from logforjob.schema import JobSearchCreate, JobSearchSession, ResumeSendCreate, ResumeSendSession
from usersetting.schema import UserSession
from utils.requestUtil import response
import jobCurd as job_curd


async def set_userguid_jobsearch(jobSearchCreate: JobSearchCreate, user: UserSession = Depends(get_user_session)):
    return JobSearchSession(**jobSearchCreate.model_dump(), user=user)


async def set_user_resume(uesumeSendCreate: ResumeSendCreate, user: UserSession = Depends(get_user_session)):
    return ResumeSendSession(**uesumeSendCreate.model_dump(), user=user)


router = APIRouter(prefix='/logforyourjobs')


@router.post("/getmainlist")
async def getmainlist(jobSearchCreate: JobSearchSession = Depends(set_userguid_jobsearch),
                      session=Depends(get_session)):
    """获取求职经历列表"""
    res = {
        "count": 0,
        "currentpage": jobSearchCreate.cpage,
        "list": []
    }
    search_list = job_curd.get_job_search_list(jobSearchCreate, session)
    if not search_list:
        return response.success("求职经历列表查询成功！", res)
    res['count'] = job_curd.get_job_search_count(jobSearchCreate, session)
    res['list'] = search_list
    return response.success("求职经历列表查询成功！", res)
    pass


@router.post("/addJobSearchLog")
async def addJobSearchLog(jobSearchSession: JobSearchSession = Depends(set_userguid_jobsearch),
                          session: Session = Depends(get_session)):
    """添加求职经历"""
    if not jobSearchSession.name:
        return response.fail(531, "求职经历名称必填！")
    if not jobSearchSession.startdate:
        return response.fail(531, "开始时间必填！")

    try:
        job_curd.add_job_search(jobSearchSession, session)
        return response.success("添加成功")
    except Exception as e:
        print(e)
        session.rollback()
        return response.fail(550, "出现异常！")


@router.post('/finishJobSeachLog')
async def finish_job_search(jobSearchSession: JobSearchSession = Depends(set_userguid_jobsearch),
                            session: Session = Depends(get_session)):
    """办结求职经历"""
    if not jobSearchSession.mguid:
        return response.fail(531, "求职经历标识必填！")
    job_search = job_curd.get_job_search_guid(jobSearchSession.mguid, session)
    if not job_search:
        return response.fail(531, f"求职经历{jobSearchSession.mguid}不存在")
    job_search.isfinish = True
    session.commit()
    return response.success("办结成功!")


@router.post('/addSendLog')
async def addSendLog(resumeSendSession: ResumeSendSession = Depends(set_user_resume),
                     session: Session = Depends(get_session)):
    """获取公司投递列表"""
    if not resumeSendSession.mguid:
        return response.fail(531, "求职记录标识必填！")
    if not resumeSendSession.cname:
        return response.fail(531, "公司名称必填！")
    if not resumeSendSession.jobname:
        return response.fail(531, "职位名称必填！")
    if not resumeSendSession.salary:
        return response.fail(531, "薪资必填！")
    if not resumeSendSession.heartlevel:
        return response.fail(531, "心动程度必填！")
    job_curd.add_resume_send(resumeSendSession, session)
    session.commit()
    session.flush()
    return response.success("新增投递记录成功!")


@router.post("/getsendList")
async def get_send_list(resumeSendSession: ResumeSendSession = Depends(set_user_resume),
                        session: Session = Depends(get_session)):
    res = {
        "count": 0,
        "currentpage": resumeSendSession.cpage,
        "list": []
    }
    search_list = job_curd.get_resume_send_list(resumeSendSession, session)
    if not search_list:
        return response.success("投递列表查询成功", res)
    res['count'] = job_curd.get_resume_send_count(resumeSendSession, session)
    res['list'] = search_list
    return response.success("投递列表查询成功", res)


@router.post('/getSendLogDetail')
async def getSendLogDetail(resumeSendSession: ResumeSendSession = Depends(set_user_resume),
                           session: Session = Depends(get_session)):
    """获取投递详情"""
    if not resumeSendSession.guid:
        return response.fail(531, "投递标识必填！")
    res = job_curd.get_resume_send_guid(resumeSendSession.guid, session)
    if not res:
        return response.fail(531, "投递详情不存在")
    return response.success("获取投递详情成功！", res)


@router.post("/deleteSendLog")
async def deleteSendLog(resumeSendSession: ResumeSendSession = Depends(set_user_resume),
                        session: Session = Depends(get_session)):
    """删除投递记录"""
    if not resumeSendSession.guid:
        return response.fail(531, "投递标识必填！")
    job_curd.delete_resume_send(resumeSendSession, session)
    session.commit()
    # session.flush()
    return response.success("删除投递记录成功!")


@router.post("/modifySendLog")
async def modify_send(resumeSendSession: ResumeSendSession = Depends(set_user_resume),
                      session: Session = Depends(get_session)):
    """修改投递记录"""
    job_curd.update_resume_send(resumeSendSession, session)
    session.commit()
    return response.success("修改投递记录成功!")
