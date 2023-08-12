class Response:
    def fail(self, code: int, msg: str, custom: dict = {}) -> dict:
        return {'state': {"code": code, "msg": msg}, "custom": custom}

    def success(self, msg: str, custom: dict = {}) -> dict:
        return {'state': {"code": '200', "msg": msg}, "custom": custom}


response = Response()
