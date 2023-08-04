import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from login import routers as login
from login import tokenRouter
from dao.database import Base, engine

app = FastAPI()
# 定义token获取的接口

app.include_router(tokenRouter.router)
app.include_router(login.router)

# //根据模型创建对饮的数据表
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
