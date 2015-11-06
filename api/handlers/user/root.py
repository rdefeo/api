from tornado.gen import engine
from tornado.web import RequestHandler, asynchronous, Finish
from tornado.escape import json_encode, json_decode

from user.data import UserData
from api.settings import ADD_CORS_HEADERS


# from api.handlers.extractors import ParamExtractor, BodyExtractor, PathExtractor
# from api.handlers.extractors import BodyExtractor
from facepy import GraphAPI


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


class Facebook(RequestHandler):
    _body_extractor = None
    _user_data = None

    def set_default_headers(self):
        if ADD_CORS_HEADERS:
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')

    def initialize(self):
        self._body_extractor = BodyExtractor(self)
        self._user_data = UserData()
        self._user_data.open_connection()

    @asynchronous
    @engine
    def options(self, *args, **kwargs):
        self.finish()

    @asynchronous
    @engine
    def post(self, *args, **kwargs):
        access_token = self._body_extractor.access_token()
        graph = GraphAPI(access_token)
        facebook_user_id = self._body_extractor.user_id()
        user = self._user_data.upsert_facebook(facebook_user_id=facebook_user_id)
        self.set_status(201)
        self.set_header("Location", "/user/%s/" % (user["_id"]))
        self.set_header("_id", str(user["_id"]))
        self.finish(
            json_encode(
                {
                    "_id": str(user["_id"])
                }
            )
        )

        if "facebook_user_data" not in user:
            facebook_user_data = graph.get("me/?fields=id,name,picture,first_name,last_name,age_range,link,locale,timezone,verified,email")
            self._user_data.upsert_facebook(_id=user["_id"],facebook_user_data=facebook_user_data, upsert=False)
