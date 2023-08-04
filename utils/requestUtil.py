class Response:
    def fail(self, code: int, msg: str, custom: dict = {}) -> dict:
        return {"code": code, "msg": msg, "custom": custom}

    def success(self, msg: str, custom: dict) -> dict:
        return {"code": '200', "msg": msg, "custom": custom}


response = Response()
