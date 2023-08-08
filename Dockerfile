FROM python:3.10-slim
MAINTAINER dml_4015
# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# 拷贝文件到容器中
COPY . /app/
EXPOSE 8000
# 设置启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
