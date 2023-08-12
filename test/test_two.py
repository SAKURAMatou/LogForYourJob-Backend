import os
import time
import unittest
import uuid
from datetime import timedelta, datetime, tzinfo
from typing import Optional

from pydantic import BaseModel, field_validator

from utils.JWTUtil import encrypt_and_expire
from utils.pathUtil import get_home_dir, get_avatar_storage_path, makedir_if_missing


def sql_page(session: str, currentPage=1, pagesize=10, orderby=None,
             order='desc', options: str = None, *columns):
    print(session, currentPage, pagesize, orderby, order, options, columns)


class Item(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator('description', 'name', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        print('empty_str_to_none', v)
        return None if v == "" else v


class TestTwo(unittest.TestCase):

    def test_field_validator(self):
        item = Item(name="", description='')
        print(item)
        sql_page(session="session-valeu", currentPage=1, pagesize=10, orderby='name')

    def test_to_dict1(self):
        l = ['rowguid', 'cname', 'jobname', 'userguid']
        print('result', {i for i in l})

    def test_timestamp(self):
        expire_duration = timedelta(minutes=60)
        expire_time = datetime.now() + expire_duration
        now = int(time.time())
        print(expire_time.timestamp(), now, int(expire_time.timestamp()) - now)
        # print(tzinfo.utcoffset(8))

    def test_path(self):
        avatar_path = get_avatar_storage_path()
        # makedir_if_missing(avatar_path)
        st = "sdad.jpg".split('.')
        file_path = os.path.join(avatar_path, f'{uuid.uuid4()}.{"sdad.jpg".split(".")[-1]}')

        print(file_path)
