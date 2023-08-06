import uvicorn
from fastapi import FastAPI, Request

from login import routers as login
from login import tokenRouter
from logforjob import jobSearchRouters
from dao.database import Base, engine
from config import get_settings
from utils.JWTUtil import refresh_token
from logforjob.models import JobSearch

app = FastAPI()


@app.middleware("http")
async def refresh_token_middleware(request: Request, call_next):
    """刷新令牌"""
    old_token = request.headers.get("Authorization")

    response = await call_next(request)
    if old_token:
        old_token = old_token.replace("Bearer ", '')
        settings = get_settings()
        res = refresh_token(old_token, settings.secret_key)
        if res:
            response.headers["token"] = res
    return response


app.include_router(tokenRouter.router)
app.include_router(login.router)
app.include_router(jobSearchRouters.router)


@app.get('/refresh')
async def refresh():
    """发现uvicorn的热部署需要请求一次接口才能完全热部署完成，"""
    pass


# //根据模型创建对饮的数据表
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
