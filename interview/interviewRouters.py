import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from dao.database import get_session
from dependencies import get_user_session
from interview.interviewCurd import get_question_page
from interview.models import InterviewQuestion, InterviewAnswer

from logger.projectLogger import logger
from interview.schema import QuestionAddParam, QuestionListParam, QuestionResponse, Questionguid, \
    QuestionDetailResponse, QuestionModifyParam
from usersetting.schema import UserSession
from utils.requestUtil import response

router = APIRouter(prefix='/interview')

tag_map = {
    "01": 'info',
    "02": 'warning',
    "03": 'error',
    "04": 'success', "05": '', "06": 'warning'
}


@router.post("/question/add")
async def add_interview_question(questionAddParam: QuestionAddParam, user: UserSession = Depends(get_user_session),
                                 session: Session = Depends(get_session)):
    try:
        interviewQuestion = InterviewQuestion(**questionAddParam.model_dump(exclude='answer'), userguid=user.rowguid)
        interviewQuestion.rowguid = uuid.uuid4()
        interviewQuestion.create_time = datetime.now()
        interviewQuestion.tag_name = questionAddParam.tagName.split(";")
        interviewQuestion.tag_value = questionAddParam.tagValue.split(";")
        session.add(interviewQuestion)
        interviewAnswer = InterviewAnswer(rowguid=uuid.uuid4(), answer_content=questionAddParam.answer,
                                          question_guid=interviewQuestion.rowguid)
        session.add(interviewAnswer)
        session.commit()
        return response.success("新增面经成功!")
    except Exception as e:
        logger.error(e)
        session.rollback()
        return response.fail(521, "新增面经失败!")


@router.post("/question/list", dependencies=[Depends(get_user_session)])
async def get_interview_question(questionListParam: QuestionListParam, session: Session = Depends(get_session)):
    res = {
        "count": 0,
        "currentpage": questionListParam.cpage,
        "list": []
    }
    # interviewQuestion = InterviewQuestion()
    # if questionListParam.keyword is not None:
    #     interviewQuestion.equal('question', questionListParam.keyword)
    # if questionListParam.tagvalue is not None:
    #     interviewQuestion.equal('tag_value', questionListParam.tagvalue)
    # list = interviewQuestion.sql_page(session, questionListParam.cpage, questionListParam.pagesize)
    # # res_list = []
    # for item in list:
    #     question = item.get("InterviewQuestion")
    #     res['list'].append(
    #         QuestionResponse(kguid=str(question.rowguid), question=question.question,
    #                          answer=question.answer.answer_content,
    #                          tagname=question.tag_name))
    # res['count'] = interviewQuestion.sql_select(session, None, func.count("*").label("count"))
    pager = get_question_page(questionListParam, session)
    for item in pager['list']:
        resItem = QuestionResponse(kguid=str(item.rowguid), question=item.question,
                                   answer=item.answer.answer_content)
        for tagname, tagvalue in zip(item.tag_name, item.tag_value):
            resItem.tagname.append({
                "tagname": tagname,
                "tagtype": tag_map.get(tagvalue)
            })
        res['list'].append(resItem)
        res['count'] = pager['count']
        # res['list'] = pager['list']
    return response.success("列表查询成功", res)


@router.post("/question/updateViewTimes", dependencies=[Depends(get_user_session)])
async def question_view_time_up(questionguid: Questionguid, session: Session = Depends(get_session)):
    question = InterviewQuestion.get_by_guid(questionguid.questionguid, session)
    question.view_times += 1
    session.commit()
    return response.success("增加浏览次数成功!")


@router.get("/question/detail/{questionguid}", dependencies=[Depends(get_user_session)])
async def get_question_detail(questionguid: str, session: Session = Depends(get_session)):
    question = InterviewQuestion.get_by_guid(questionguid, session)
    question_detail_response = QuestionDetailResponse(rowguid=str(question.rowguid), question=question.question,
                                                      answer=question.answer.answer_content,
                                                      tagvalue=question.tag_value)
    return response.success("详情查询成功", question_detail_response)


@router.post("/question/delete", dependencies=[Depends(get_user_session)])
async def delete_question(questionguid: Questionguid, session: Session = Depends(get_session)):
    question = InterviewQuestion.get_by_guid(questionguid.questionguid, session)
    question.isdel = True
    session.commit()
    return response.success("删除成功!")


@router.post("/question/modifty", dependencies=[Depends(get_user_session)])
async def modify_question(questionModifyParam: QuestionModifyParam, session: Session = Depends(get_session)):
    question = InterviewQuestion.get_by_guid(questionModifyParam.rowguid, session)
    if questionModifyParam.answer is not None:
        question.answer.answer_content = questionModifyParam.answer
    if questionModifyParam.tagName is not None:
        question.tag_name = questionModifyParam.tagName.split(";")
    if questionModifyParam.tagValue is not None:
        question.tag_value = questionModifyParam.tagValue.split(";")
    session.commit()
    return response.success("修改成功!")
