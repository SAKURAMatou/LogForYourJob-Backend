from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from config import get_database

# 获取数据库连接信息
database_setting = get_database()

# 创建sqlalchemy的Engine对象;数据库连接池大小5，超过5个之后最多再创建10个连接
engine = create_engine(database_setting.database_url, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=1800)
# 创建数据库会话。数据库会话是与数据库进行交互的主要接口，我们可以使用会话来执行数据库查询、插入、更新和删除等操作。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# sqlalchemy的表实体的基类，用于根据表实体在数据库创建对应的表结构
# Base = declarative_base()
class Base(DeclarativeBase):
    pass


# @contextmanager
def get_session():
    """获取数据库会话的方法依赖"""
    # try:
    #     session = SessionLocal()
    #     yield session
    #     session.commit()
    # except Exception as e:
    #     print(e)
    #     session.rollback()
    # finally:
    #     session.close()
    with SessionLocal() as session:
        yield session
