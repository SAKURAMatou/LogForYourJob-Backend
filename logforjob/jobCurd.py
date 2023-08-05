from datetime import datetime
from uuid import uuid4

from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session, Query

from logforjob.schema import JobSearchSession, JobSearchBase
from logforjob.models import JobSearch


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
    sql = select(JobSearch).where(JobSearch.rowguid == guid)
    return session.execute(sql).scalar()


def get_job_search_list(jobSearchSession: JobSearchSession, session: Session) -> list[JobSearch]:
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
    # query = session.query(JobSearch).where(JobSearch.rowguid == jobSearchSession.user.rowguid)
    # if jobSearchSession.name:
    #     query = query.where(JobSearch.search_name.like(f'%{jobSearchSession.name}%'))
    # if jobSearchSession.startdate:
    #     query = query.where(JobSearch.starttime >= jobSearchSession.startdate)
    # if jobSearchSession.enddate:
    #     query = query.where(JobSearch.starttime <= jobSearchSession.startdate)
    #
    # return query.count()
    query = select(func.count("*").label("count")).select_from(JobSearch).where(
        JobSearch.userguid == jobSearchSession.user.rowguid)
    if jobSearchSession.name:
        query = query.where(JobSearch.search_name.like(f'%{jobSearchSession.name}%'))
    if jobSearchSession.startdate:
        query = query.where(JobSearch.starttime >= jobSearchSession.startdate)
    if jobSearchSession.enddate:
        query = query.where(JobSearch.starttime <= jobSearchSession.startdate)
    return session.execute(query).scalar()
