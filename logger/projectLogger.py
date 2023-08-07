import os

from loguru import logger

current_file_path = os.path.abspath(__file__)
# 循环回溯到工程的根目录（这假设你的根目录有一个特定的标识，比如 '.env' 文件或其他）
while not os.path.exists(os.path.join(current_file_path, '.root')):
    current_file_path = os.path.dirname(current_file_path)
project_root = current_file_path

# 指定 `applog` 文件夹路径
applog_folder = os.path.join(project_root, "applog")
# 如果文件夹不存在，创建它
if not os.path.exists(applog_folder):
    os.makedirs(applog_folder)

# 设置日志文件路径


log_file_path = os.path.join(applog_folder, 'logger_{time:YYYY_MM_DD}.log')
# serialize=True:日志在传递给loguru的日志接收器之前都会序列化为json,包含很多线程等信息
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | {level} |  <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>"

logger.add(log_file_path, format=log_format, rotation='100 MB',
           backtrace=True, level="INFO")
