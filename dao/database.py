from typing import Any, List

from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Select, and_, select, desc, asc, CursorResult, RowMapping, text, inspect
from contextlib import contextmanager

from sqlalchemy.sql.base import ExecutableOption

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
    def __init__(self, **kw: Any):
        super().__init__()
        for key, value in kw.items():
            setattr(self, key, value)
        self._like_conditions: list[{}] = []
        self._less_conditions: list[{}] = []
        self._great_conditions: list[{}] = []
        self._equal_conditions: list[{}] = []
        self._text_sql: list[str] = []

    def equal(self, columns, value):
        self._equal_conditions.append({columns: value})

    def less(self, columns, value):
        self._less_conditions.append({columns: value})

    def great(self, columns, value):
        self._great_conditions.append({columns: value})

    def like(self, columns, value: str):
        if not (value.startswith('%') and value.endswith('%')):
            self._like_conditions.append({columns: f'%{value}%'})
        else:
            self._like_conditions.append({columns: value})

    def text_sql(self, value: str):
        self._text_sql.append(value)

    def to_dict(self):
        """ROM转dict，排除空值"""
        data = {}
        for c in self.__table__.columns:
            v = getattr(self, c.name)
            if v is not None:
                data[c.name] = v
        return data

    def to_dict_all(self):
        """ORM转dict，全字段"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def get_columns(cls) -> list[str]:
        """获取当前表实体的所有列名"""
        inspector = inspect(cls)
        return [column.key for column in inspector.attrs]

    def where_condition(self) -> list:
        conditions = []
        columns = self.__table__.columns
        if len(self._equal_conditions) > 0:
            for i in self._equal_conditions:
                for key, value in i.items():
                    conditions.append(columns[key] == value)
        if len(self._less_conditions) > 0:
            for i in self._less_conditions:
                for key, value in i.items():
                    conditions.append(columns[key] < value)
        if len(self._great_conditions) > 0:
            for i in self._great_conditions:
                for key, value in i.items():
                    conditions.append(columns[key] > value)
        if len(self._like_conditions) > 0:
            for i in self._like_conditions:
                for key, value in i.items():
                    conditions.append(columns[key].like(value))
        if len(self._text_sql) > 0:
            for i in self._text_sql:
                conditions.append(text(i))

        return conditions

    def sql_select(self, session: Session, options: ExecutableOption, *columns) -> CursorResult:
        """
        执行select语句，select的返回结果比较多样，方法直接返回CursorResult，需要对函数返回值进行后续操作，需要列表时需要手动执行all，需要单个值的话执行scalar;
        查询count时传入对应的count表达式，例如func.count("*").label("count")
        """
        if not columns:
            columns = self.__class__

        # 获取搜索条件列表
        conditions = self.where_condition()
        sql = select(*columns).select_from(self.__table__)
        if options:
            sql = sql.options(options)

        if len(conditions) > 0:
            sql = sql.where(and_(*conditions))
        return session.execute(sql)

    def sql_page(self, session: Session, currentPage=1, pagesize=10, orderby=None,
                 order='desc', options: ExecutableOption = None, *columns) -> list[RowMapping]:
        """分页查询数据；返回结果是list[RowMapping]，通用查询方法，没有指定model，返回结果默认是Row，
        row类型类似tuple没有__dict__的默认函数，直接作为返回值会有异常
        ；默认值：currentPage=1, pagesize=10, order='desc'"""
        if len(columns) > 0:
            # columns = self.__table__.columns
            sql = select(*columns).select_from(self.__table__)
        else:
            sql = select(self.__class__)

        if options:
            sql = sql.options(options)
        # 获取搜索条件列表
        conditions = self.where_condition()
        # conditions = []
        # sql = select(*columns).select_from(self.__table__)
        if len(conditions) > 0:
            sql = sql.where(and_(*conditions))
        if orderby:
            if 'desc' == order:
                sql = sql.order_by(desc(orderby))
            else:
                sql = sql.order_by(asc(orderby))
        if all([currentPage, pagesize]):
            sql = sql.limit(pagesize).offset((currentPage - 1) * pagesize)
        res = session.execute(sql).all()
        # return res
        return [row._mapping for row in res]

    @classmethod
    def get_by_guid(cls, guid: str, session: Session, options: ExecutableOption, *columns) -> Any:
        """
        类方法，不是属性方法，根据主键查询一条表记录;
        option:查询条件"""
        inspector = inspect(cls)
        sql = select(cls)
        if len(columns) > 0:
            sql = select(*columns).select_from(cls.__table__)
        if options:
            sql = sql.options(options)
        # inspector包含了表实体的信息，inspector.primary_key是一个tuple类型记录了主键列
        sql = sql.where(inspector.primary_key[0] == guid)
        return session.scalar(sql)

    def update_self_value(self, waitUpdate: dict):
        """根据传入的字典修改对应的属性值，不会更新数据库的值，需要提交事务则手动执行session.commit()"""
        # noNone = {k: v for k, v in waitUpdate.items() if v is not None}
        for k, v in waitUpdate.items():
            if v:
                setattr(self, k, v)


def get_session():
    with SessionLocal() as session:
        yield session

    # @contextmanager
    # def get_session():
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
