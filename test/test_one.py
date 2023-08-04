import unittest
import uuid
from datetime import datetime, timedelta
import time

from utils.JWTUtil import encrypt_and_expire, decrypt_and_check_expiration, decrypt_token, hash_pwd, check_password


class TestOne(unittest.TestCase):
    def test_uuid4(self):
        uid = uuid.uuid4()
        print('time', uid.time, type(uid.time))
        print('int', uid.int, type(uid.int))
        print('bytes', uid.bytes, type(uid.bytes))
        print('hex', uid.hex, type(uid.hex))
        print('urn', uid.urn, type(uid.urn))
        print('str', str(uid), type(str(uid)) == str)

    def test_time(self):
        now = datetime.now()
        expire_time = now + timedelta(minutes=5)
        print(now, expire_time)

    def test_time(self):
        now = int(time.time())
        print(now)
        timeArray = time.localtime(now)
        print(timeArray)
        print(type(datetime.now()))
        print(type(time.time()))

    def test_jwtUtill_decrypt(self):
        token = encrypt_and_expire('dec65e9c-cb80-46cd-a7fc-1b5edf9e4a02', 'dml_activity_key', 10)
        print(token)
        time.sleep(10)
        payload = decrypt_token(token, 'dml_activity_key')
        print('now', int(time.time()))
        print(payload['exp'], datetime.fromtimestamp(payload['exp']))
        print(decrypt_and_check_expiration(token, 'dml_activity_key'))

    def test_hash_pwd(self):
        hashed = hash_pwd("11111")
        print(type(hashed), str(hashed))
        print(
            check_password('11111', 'JDJiJDEyJFM5c254a2t2VzRTOHlNa0MxLmVzZ3VWVko3ckhRMkZ2NUxrQmxjQ3NLNUxnSkR3QndKMjhX'))

    def test_time_diff(self):
        end = datetime.now() + timedelta(minutes=5)
        dif = end.timestamp() - time.time()
        print(round(dif))
        if "test":
            print('test')
