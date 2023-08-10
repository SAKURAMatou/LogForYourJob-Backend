import sys

import uvicorn
import logging
from fastapi import FastAPI, Request

from login import routers as login
from login import tokenRouter
from logforjob import jobSearchRouters
from dao.database import Base, engine
from config import get_settings
from utils.JWTUtil import refresh_token
from logger.projectLogger import logger

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

from loguru import logger


# 把fastapi、uvicorn的日志拦截并交给Loguru进入打印
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0)

# Redirect Uvicorn logs
for name in ("uvicorn", "uvicorn.error", 'uvicorn.access', "fastapi"):
    logging_logger = logging.getLogger(name)
    logging_logger.handlers = [InterceptHandler()]


@app.get('/refresh')
async def refresh():
    """发现uvicorn的热部署需要请求一次接口才能完全热部署完成，"""
    pass


def setup_logging():
    """logurn的配置函数"""
    pass


setup_logging()

# //根据模型创建对饮的数据表
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True,
                reload_dirs=["utils", "usersetting", "login", "logforjob", 'dao'])
