from fastapi import APIRouter, Depends

from dao.database import get_session
from dependencies import get_user_session
from logforjob.schema import JobSearchCreate, JobSearchSession, ResumeSendCreate, ResumeSendSession
from usersetting.schema import UserSession


async def set_userguid_jobsearch(jobSearchCreate: JobSearchCreate, user: UserSession = Depends(get_user_session)):
    return JobSearchSession(**jobSearchCreate.model_dump(), user=user)


async def set_user_resume(uesumeSendCreate: ResumeSendCreate, user: UserSession = Depends(get_user_session)):
    return ResumeSendSession(**uesumeSendCreate.model_dump(), user=user)


router = APIRouter(prefix='/logforyourjobs')


@router.post("/getmainlist")
async def getmainlist(jobSearchCreate: JobSearchSession = Depends(set_userguid_jobsearch),
                      session=Depends(get_session)):
    print(jobSearchCreate)
    pass


