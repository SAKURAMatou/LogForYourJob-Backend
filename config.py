"""系统配置"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv


class DatabaseSettings(BaseSettings):
    """数据库连接信息"""
    model_config = SettingsConfigDict(env_file_encoding='utf-8', extra='ignore')
    database_url: str
    #
    # database_username: str
    # database_password: str


class Settings(BaseSettings):
    """系统配置"""
    model_config = SettingsConfigDict(env_file_encoding='utf-8', extra='ignore')
    secret_key: str  # 用户token的加密key
    activity_key: str  # 用户激活时的加密key
    system_host: str
    smtp_port: int
    token_expires_in: int = 60
    fornt_host: str
    smtp_server: str
    smtp_username: str
    smtp_password: str


@lru_cache()
def get_database() -> DatabaseSettings:
    # load_dotenv('.env.database')
    return DatabaseSettings(_env_file='.env.database')


@lru_cache()
def get_settings() -> Settings:
    return Settings(_env_file='.env')
