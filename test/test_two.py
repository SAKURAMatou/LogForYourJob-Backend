import unittest


class TestTwo(unittest.TestCase):
    def test_to_dict1(self):
        l = ['rowguid', 'cname', 'jobname', 'userguid']
        print('result', {i for i in l})
