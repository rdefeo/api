from bson import ObjectId
from bson.errors import InvalidId
from tornado.escape import json_encode, json_decode
from tornado.web import RequestHandler, Finish
from tornado.websocket import WebSocketHandler


# class CookieExtractor:
#     def __init__(self, handler: RequestHandler):
#         self.handler = handler
#
#     def user_id(self) -> ObjectId:
#         raw_user_id = self.handler.get_cookie("user_id", None)
#         try:
#             return ObjectId(raw_user_id) if raw_user_id is not None else None
#         except InvalidId:
#             self.handler.set_status(428, "invalid cookie=user_id,user_id=%s" % raw_user_id)
#             raise Finish()


class BodyExtractor:
    def __init__(self, handler: RequestHandler):
        self.handler = handler

    def body(self) -> dict:
        try:
            return json_decode(self.handler.request.body.decode("utf-8"))
        except:
            self.handler.set_status(412)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid body,body=%s" % self.handler.request.body
                    }
                )
            )
            raise Finish()

    def user_id(self):
        if "userID" not in self.authResponse():
            self.handler.set_status(412)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing,authResponse[userID]"
                    }
                )
            )
            raise Finish()
        else:
            return self.authResponse()["userID"]


    def authResponse(self) -> dict:
        if "authResponse" not in self.body():
            self.handler.set_status(412)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing,authResponse"
                    }
                )
            )
            raise Finish()
        else:
            return self.body()["authResponse"]

    def access_token(self):
        if "accessToken" not in self.authResponse():
            self.handler.set_status(412)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing,authResponse[accessToken]"
                    }
                )
            )
            raise Finish()
        else:
            return self.authResponse()["accessToken"]


class WebSocketCookieExtractor:
    def __init__(self, handler: WebSocketHandler):
        self._handler = handler

    def application_id(self) -> ObjectId:
        raw_application_id = self._handler.get_cookie("application_id", None)
        if raw_application_id is None:
            raise Exception("missing param(s) application_id")
        try:
            return ObjectId(raw_application_id)
        except InvalidId:
            raise Exception("missing param(s) application_id")

    def session_id(self) -> ObjectId:
        raw_session_id = self._handler.get_cookie("session_id", None)
        if raw_session_id is None:
            raise Exception("missing param(s) session_id")
        try:
            return ObjectId(raw_session_id)
        except InvalidId:
            raise Exception("missing param(s) session_id")

    def user_id(self) -> ObjectId:
        raw_user_id = self._handler.get_cookie("user_id", None)
        try:
            return ObjectId(raw_user_id) if raw_user_id is not None else None
        except InvalidId:
            raise Exception("missing param(s) user_id")



class ParamExtractor:
    def __init__(self, handler: RequestHandler):
        self.handler = handler
        pass

    def session_id(self) -> ObjectId:
        raw_session_id = self.handler.get_argument("session_id", None)
        if raw_session_id is None:
            self.handler.set_status(428, "missing param(s) session_id")
            raise Finish()

        try:
            return ObjectId(raw_session_id)
        except InvalidId:
            self.handler.set_status(412)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=session_id,session_id=%s" % raw_session_id
                    }
                )
            )
            raise Finish()

    def application_id(self) -> ObjectId:
        raw_application_id = self.handler.get_argument("application_id", None)
        if raw_application_id is None:
            self.handler.set_status(428, "missing param(s) application_id")
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing param(s) application_id"
                    }
                )
            )
            raise Finish()

        try:
            return ObjectId(raw_application_id)
        except InvalidId:
            self.handler.set_status(412)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=application_id,application_id=%s" %
                                   raw_application_id
                    }
                )
            )
            raise Finish()

    def user_id(self) -> ObjectId:
        raw_user_id = self.handler.get_argument("user_id", None)
        try:
            return ObjectId(raw_user_id) if raw_user_id is not None else None
        except InvalidId:
            self.handler.set_status(428)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=user_id,user_id=%s" % raw_user_id
                    }
                )
            )
            raise Finish()

    def suggest_id(self) -> ObjectId:
        raw_suggest_id = self.handler.get_argument("suggest_id", None)
        try:
            return ObjectId(raw_suggest_id) if raw_suggest_id is not None else None
        except InvalidId:
            self.handler.set_status(428)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=suggest_id,suggest_id=%s" % raw_suggest_id
                    }
                )
            )
            raise Finish()

    def context_id(self) -> ObjectId:
        raw_context_id = self.handler.get_argument("context_id", None)
        try:
            return ObjectId(raw_context_id) if raw_context_id is not None else None
        except InvalidId:
            self.handler.set_status(428)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=context_id,context_id=%s" % raw_context_id
                    }
                )
            )
            raise Finish()

    def locale(self) -> str:
        locale = self.handler.get_argument("locale", None)
        if locale is None:
            self.handler.set_status(428)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing param=locale"
                    }
                )
            )
            raise Finish()
        else:
            return locale
