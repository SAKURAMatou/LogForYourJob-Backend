from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from dao.database import get_session
from dependencies import get_user_session
from logforjob import jobCurd as job_curd
from logforjob.models import ResumeSend
from logforjob.schema import JobSearchCreate, JobSearchSession, ResumeSendCreate, ResumeSendSession, JobSearchResponse, \
    ResumeSendResponse
from usersetting.schema import UserSession
from utils.requestUtil import response


async def set_userguid_jobsearch(jobSearchCreate: JobSearchCreate, user: UserSession = Depends(get_user_session)):
    return JobSearchSession(**jobSearchCreate.model_dump(), user=user)


async def set_user_resume(uesumeSendCreate: ResumeSendCreate, user: UserSession = Depends(get_user_session)):
    return ResumeSendSession(**uesumeSendCreate.model_dump(), user=user)


router = APIRouter(prefix='/logforyourjobs')


@router.post("/getmainlist")
async def getmainlist(jobSearchCreate: JobSearchSession = Depends(set_userguid_jobsearch),
                      session: Session = Depends(get_session)):
    """获取求职经历列表"""
    res = {
        "count": 0,
        "currentpage": jobSearchCreate.cpage,
        "list": []
    }

    search_list = job_curd.get_job_search_list(jobSearchCreate, session).all()

    if not search_list and len(search_list) > 0:
        return response.success("求职经历列表查询成功！", res)

    res_list = []
    for item in search_list:
        res_item = JobSearchResponse(guid=item.rowguid, name=item.search_name)
        res_item.isend = '1' if item.isfinish else '0'
        if item.starttime:
            res_item.startdate = item.starttime.strftime('%Y-%m-%d')
        else:
            res_item.startdate = '--'
        if item.endtime:
            res_item.enddate = item.endtime.strftime('%Y-%m-%d')
        else:
            res_item.enddate = '--'
        res_list.append(res_item)

    res['count'] = job_curd.get_job_search_count(jobSearchCreate, session)
    res['list'] = res_list
    return response.success("求职经历列表查询成功！", res)


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
    """获取求职经历列表,分页；要求入参必须有对应的mguid"""
    if not resumeSendSession.mguid:
        response.fail(531, 'mguid必填！')
    res = {
        "count": 0,
        "currentpage": resumeSendSession.cpage,
        "list": []
    }
    resumeSend = ResumeSend()
    # 搜索条件
    # dump = resumeSendSession.model_dump(include=resumeSend.to_dict_all().keys())
    if resumeSendSession.startdate:
        resumeSend.great('sendtime', resumeSendSession.staredate)
    if resumeSendSession.enddate:
        resumeSend.less('sendtime', resumeSendSession.enddate)
    if resumeSendSession.cname:
        resumeSend.like('cname', resumeSendSession.cname)
    if resumeSendSession.heartlevel:
        resumeSend.equal('heartlevel', resumeSendSession.heartlevel)
    if resumeSendSession.salarydown:
        resumeSend.great('salary', resumeSendSession.salary)
    if resumeSendSession.salaryup:
        resumeSend.less('salary', resumeSendSession.salary)

    # 默认条件时没有删除的数据
    resumeSend.equal('mguid', resumeSendSession.mguid)
    resumeSend.equal('isdel', False)

    search_list = resumeSend.sql_page(session, resumeSendSession.cpage,
                                      resumeSendSession.pagesize,
                                      'sendtime')
    # search_list = session.scalar(sql)
    if not search_list:
        return response.success("求职经历列表查询成功！", res)

    res_lsit = []
    for resItem in search_list:

        if isinstance(resItem.get("ResumeSend"), ResumeSend):
            item = ResumeSendResponse(**resItem.get("ResumeSend").to_dict())
            item.guid = resItem.get("ResumeSend").rowguid
            item.mname = resItem.get("ResumeSend").job_search.search_name
            if isinstance(item.sendtime, datetime):
                item.sendtime = item.sendtime.strftime('%Y-%m-%d %H:%M')
            res_lsit.append(item)
        else:
            item = ResumeSendResponse()
            item.guid = resItem.get("ResumeSend").rowguid
            item.cname = resItem.get("ResumeSend").cname
            item.heartlevel = resItem.get("ResumeSend").heartlevel
            if resItem.get("ResumeSend").sendtime:
                item.sendtime = resItem.get("ResumeSend").sendtime.strftime('%Y-%m-%d %H:%M:%S')
            item.jobname = resItem.get("ResumeSend").jobname
            item.salary = str(resItem.get("ResumeSend").salary)
            item.requirement = resItem.get("ResumeSend").requirement
            item.mguid = resItem.get("ResumeSend").mguid
            item.mname = resItem.get("ResumeSend").job_search.search_name
            res_lsit.append(item)

    count_sql = resumeSend.sql_select(session, None, func.count("*").label("count"))
    res['count'] = count_sql.scalar()
    res['list'] = res_lsit

    return response.success("投递列表查询成功", res)


@router.post('/getSendLogDetail')
async def getSendLogDetail(resumeSendSession: ResumeSendSession = Depends(set_user_resume),
                           session: Session = Depends(get_session)):
    """获取投递详情"""
    if not resumeSendSession.guid:
        return response.fail(531, "投递标识必填！")
    # res = job_curd.get_resume_send_guid(resumeSendSession.guid, session)
    res = ResumeSend.get_by_guid(resumeSendSession.guid, session, options=joinedload(ResumeSend.job_search))
    if not res:
        return response.fail(531, "投递详情不存在")
    resumeSendResponse = ResumeSendResponse(**res.to_dict())
    resumeSendResponse.guid = res.rowguid
    resumeSendResponse.mname = res.job_search.search_name
    return response.success("获取投递详情成功！", resumeSendResponse)


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
    if not resumeSendSession.guid:
        return response.fail("投递标识必填！")
    # job_curd.update_resume_send(resumeSendSession, session)
    resume_send = ResumeSend.get_by_guid(resumeSendSession.guid, session)
    if not resume_send:
        return response.fail(533, "数据不存在！")

    update_colums = resumeSendSession.model_dump(include=ResumeSend.get_columns())
    resume_send.update_self_value(update_colums)
    session.commit()
    return response.success("修改投递记录成功!")
