import uvicorn
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()
# 定义token获取的接口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="rest/token")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
