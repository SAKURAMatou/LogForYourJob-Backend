import sys

import logging
from datetime import datetime

from fastapi.security.utils import get_authorization_scheme_param
from loguru import logger
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from login import routers as login
from login import tokenRouter
from logforjob import jobSearchRouters
from dao.database import Base, engine
from config import get_settings
from utils.JWTUtil import refresh_token
from usersetting import usersRouter

app = FastAPI()


@app.middleware("http")
async def refresh_token_middleware(request: Request, call_next):
    """刷新令牌"""
    starttime = datetime.now()
    old_token = request.headers.get("Authorization")
    token = request.cookies.get("token")
    if token is not None:
        # Authorization的token从请求头和cookie两个地方获取
        old_token = token

    response = await call_next(request)
    if '/user/logout' == request.url.path:
        # 退出登录时需要清空cookie
        response.set_cookie(key='token', value='', httponly=True, max_age=0)
        return response
    else:
        # 解析出token的值,当入参为空时返回("","")
        scheme, param = get_authorization_scheme_param(old_token)
        if scheme.lower() == 'bearer':
            # old_token = old_token.replace("Bearer ", '')
            old_token = param
            settings = get_settings()
            res = refresh_token(old_token, settings.secret_key)
            if res:
                # response.headers["token"] = res
                response.set_cookie(key='token', value=f'Bearer {res}',
                                    httponly=True, max_age=settings.token_expires_in * 60)
    timelong = datetime.now() - starttime
    logger.info(f"请求{request.url.path}耗时:{timelong}ms;{timelong / 1000}s")
    return response


app.include_router(tokenRouter.router)
app.include_router(login.router)
app.include_router(jobSearchRouters.router)
app.include_router(usersRouter.router)

# 设置头像访问的静态文件服务
app.mount("/avatars", StaticFiles(directory="storage/avatar"), name="avatars")


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


@app.get('/refresh')
async def refresh():
    """发现uvicorn的热部署需要请求一次接口才能完全热部署完成，"""
    pass


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')


def setup_logging():
    """logurn的配置函数"""
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # Redirect Uvicorn logs
    for name in ("uvicorn", "uvicorn.error", 'uvicorn.access', "fastapi"):
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]


# 把uvicorn的日志转移到logurn进行统一的日志打印
setup_logging()
# //根据模型创建对饮的数据表
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # 本地调试代码
    import uvicorn

    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True,
                reload_dirs=["utils", "usersetting", "login", "logforjob", 'dao'])
