from bson import ObjectId
from bson.errors import InvalidId
from tornado.escape import json_encode
from tornado.web import RequestHandler, Finish


class ParamExtractor:
    def __init__(self, handler: RequestHandler):
        self.handler = handler
        pass

    def session_id(self) -> ObjectId:
        raw_session_id = self.handler.get_argument("session_id", None)
        if raw_session_id is None:
            self.handler.set_status(428)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing param(s) session_id"
                    }
                )
            )
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
            self.handler.set_status(428)
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