from datetime import datetime
from uuid import uuid4

from sqlalchemy import select, desc, func, update
from sqlalchemy.orm import Session, Query

from logforjob.schema import JobSearchSession, JobSearchBase, ResumeSendSession
from logforjob.models import JobSearch, ResumeSend


def add_job_search(jobSearchCreate: JobSearchSession, session: Session):
    """添加求职经历"""
    jobSearch = JobSearch(rowguid=str(uuid4()), userguid=jobSearchCreate.user.rowguid)
    jobSearch.search_name = jobSearchCreate.name
    jobSearch.starttime = jobSearchCreate.startdate
    jobSearch.isfinish = False
    session.add(jobSearch)
    session.commit()
    session.flush()
    print(jobSearch)


def get_job_search_guid(guid: str, session: Session) -> JobSearch:
    """根据主键查找求职经历job_search"""
    sql = select(JobSearch).where(JobSearch.rowguid == guid)
    return session.execute(sql).scalar()


def get_job_search_list(jobSearchSession: JobSearchSession, session: Session) -> list[JobSearch]:
    """获取求职经历列表，分页"""
    sql = select(JobSearch).where(JobSearch.userguid == jobSearchSession.user.rowguid)
    page_size = jobSearchSession.pagesize
    page_number = jobSearchSession.cpage
    offset = (page_number - 1) * page_size
    if jobSearchSession.name:
        sql = sql.where(JobSearch.search_name.like(f'%{jobSearchSession.name}%'))
    if jobSearchSession.startdate:
        sql = sql.where(JobSearch.starttime >= jobSearchSession.startdate)
    if jobSearchSession.enddate:
        sql = sql.where(JobSearch.starttime <= jobSearchSession.startdate)

    sql = sql.order_by(desc(JobSearch.starttime)).offset(offset).limit(page_size)

    return session.scalars(sql).all()


def get_job_search_count(jobSearchSession: JobSearchSession, session: Session) -> int:
    """求职经历总数"""
    query = select(func.count("*").label("count")).select_from(JobSearch).where(
        JobSearch.userguid == jobSearchSession.user.rowguid)
    if jobSearchSession.name:
        query = query.where(JobSearch.search_name.like(f'%{jobSearchSession.name}%'))
    if jobSearchSession.startdate:
        query = query.where(JobSearch.starttime >= jobSearchSession.startdate)
    if jobSearchSession.enddate:
        query = query.where(JobSearch.starttime <= jobSearchSession.startdate)
    return session.execute(query).scalar()


def get_resume_send_list(resumeSendSession: ResumeSendSession, session: Session) -> list[ResumeSend]:
    """查询投递列表，分页"""
    return None


def get_resume_send_count(resumeSendSession: ResumeSendSession, session: Session) -> int:
    """投递总数"""

    return 0


def add_resume_send(resumeSendSession: ResumeSendSession, session: Session):
    """添加投递记录"""
    resumeSend = ResumeSend(**resumeSendSession.model_dump())
    resumeSend.rowguid = str(uuid4())
    resumeSend.sendtime = datetime.now()
    resumeSend.userguid = resumeSendSession.user.rowguid
    session.add(resumeSend)


def get_resume_send_guid(guid: str, session: Session) -> ResumeSend:
    """根据主键获取投递详情"""
    sql = select(ResumeSend).where(ResumeSend.rowguid == guid)
    return session.scalars(sql)


def delete_resume_send(resumeSendSession: ResumeSendSession, session: Session):
    """删除投递记录,逻辑删除，不是物理删除"""
    sql = update(ResumeSend).where(ResumeSend.rowguid == resumeSendSession.guid).values(ResumeSend.isdel == True)
    session.execute(sql)


def update_resume_send(resumeSendSession: ResumeSendSession, session: Session):
    """更新数据"""
    sql = update(ResumeSend).where(ResumeSend.rowguid == resumeSendSession.guid)
    # 入参转化为dict只保留ORM中有的字段
    dump = resumeSendSession.model_dump(include=ResumeSend().to_dict_all().keys())
    # 排除掉需要更新的字段中的空值
    sql = sql.values({k: v for k, v in dump.items() if v is not None})
    print(sql)
    return None
