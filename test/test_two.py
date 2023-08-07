import time
import unittest
from datetime import timedelta, datetime, tzinfo

from utils.JWTUtil import encrypt_and_expire


class TestTwo(unittest.TestCase):
    def test_to_dict1(self):
        l = ['rowguid', 'cname', 'jobname', 'userguid']
        print('result', {i for i in l})

    def test_timestamp(self):
        expire_duration = timedelta(minutes=60)
        expire_time = datetime.now() + expire_duration
        now = int(time.time())
        print(expire_time.timestamp(), now, int(expire_time.timestamp()) - now)
        # print(tzinfo.utcoffset(8))
