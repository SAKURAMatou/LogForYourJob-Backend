import unittest
import uuid


class TestOne(unittest.TestCase):
    def test_uuid4(self):
        uid = uuid.uuid4()
        print('time', uid.time, type(uid.time))
        print('int', uid.int, type(uid.int))
        print('bytes', uid.bytes, type(uid.bytes))
        print('hex', uid.hex, type(uid.hex))
        print('urn', uid.urn, type(uid.urn))
        print('str', str(uid), type(str(uid)))
