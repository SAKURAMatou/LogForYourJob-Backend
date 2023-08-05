from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from logforjob.schema import JobSearchSession
from logforjob.models import JobSearch


def add_job_search(jobSearchCreate: JobSearchSession, session: Session):
    """添加求职经历"""
    jobSearch = JobSearch(rowguid=str(uuid4()), userguid=jobSearchCreate.user.rowguid)
    jobSearch.search_name = jobSearchCreate.mname
    jobSearch.starttime = jobSearchCreate.startdate
    jobSearch.isfinish = False
    session.add(jobSearch)
    session.commit()
    session.flush()
    print(jobSearch)
