"""系统配置"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv


# load_dotenv()


class DatabaseSettings(BaseSettings):
    """数据库连接信息"""
    model_config = SettingsConfigDict(env_file_encoding='utf-8', extra='ignore')
    database_url: str
    #
    # database_username: str
    # database_password: str


@lru_cache()
def get_database():
    load_dotenv('.env.database')
    return DatabaseSettings(_env_file='.env.database')
