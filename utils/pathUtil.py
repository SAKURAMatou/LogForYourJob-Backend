import os
from datetime import datetime


def get_home_dir():
    current_file_path = os.path.abspath(__file__)
    # 循环回溯到工程的根目录（这假设你的根目录有一个特定的标识，比如 '.env' 文件或其他）
    while not os.path.exists(os.path.join(current_file_path, '.root')):
        current_file_path = os.path.dirname(current_file_path)
    return current_file_path


def makedir_if_missing(path: str, from_home: bool = False) -> str:
    """创建文件夹，如果不存在的话"""
    if from_home:
        path = os.path.join(get_home_dir(), path)
    if not os.path.exists(path):
        os.makedirs(path)
    # sleep(5)
    return path


def get_file_storage_path():
    """获取附件存储路径"""
    timestr = datetime.now().strftime('%Y_%m_%d')
    return os.path.join(get_home_dir(), 'storage', 'files', timestr)


def get_avatar_storage_path():
    """获取头像存储的路径"""
    timestr = datetime.now().strftime('%Y_%m_%d')
    return os.path.join(get_home_dir(), 'storage', 'avatar', timestr)
