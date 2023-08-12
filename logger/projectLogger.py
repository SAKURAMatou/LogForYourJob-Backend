import os

from loguru import logger

from utils.pathUtil import get_home_dir, makedir_if_missing

# 指定 工程根目录/applog为日志 文件夹路径
applog_folder = makedir_if_missing("applog", from_home=True)

log_file_path = os.path.join(applog_folder, 'logger_{time:YYYY_MM_DD}.log')
# serialize=True:日志在传递给loguru的日志接收器之前都会序列化为json,包含很多线程等信息
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | {level} |  <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>"

logger.add(log_file_path, format=log_format, rotation='100 MB',
           backtrace=True, level="INFO")
