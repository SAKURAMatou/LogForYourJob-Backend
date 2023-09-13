from sqlalchemy import text, select, func
from sqlalchemy.orm import Session

from interview.models import InterviewQuestion
from interview.schema import QuestionListParam


def get_question_page(questionListParam: QuestionListParam, session: Session) -> dict:
    sql = select(InterviewQuestion).where(InterviewQuestion.isdel == False)
    count_sql = select(func.count("*").label("count")).select_from(InterviewQuestion).where(
        InterviewQuestion.isdel == False)
    if questionListParam.tagvalue is not None:
        tag_values = questionListParam.tagvalue.split(";")
        for i in tag_values:
            sql = sql.where(InterviewQuestion.tag_value.any(i))
            count_sql = count_sql.where(InterviewQuestion.tag_value.any(i))
    if questionListParam.keyword is not None:
        sql = sql.where(InterviewQuestion.question.like(f"%{questionListParam.keyword}%"))
        count_sql = count_sql.where(InterviewQuestion.question.like(f"%{questionListParam.keyword}%"))

    sql = sql.order_by(InterviewQuestion.create_time.desc()).order_by(InterviewQuestion.view_times.asc()).limit(
        questionListParam.pagesize).offset(
        (questionListParam.cpage - 1) * questionListParam.pagesize)
    list = session.scalars(sql).all()
    count = session.execute(count_sql).scalar()
    return {"list": list, "count": count}
