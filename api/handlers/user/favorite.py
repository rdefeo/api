from bson import ObjectId
from bson.errors import InvalidId
from tornado.gen import engine
from tornado.web import RequestHandler, asynchronous, Finish

from tornado.escape import json_encode, json_decode

from user.data import FavoriteData
from api.settings import ADD_CORS_HEADERS

class PathExtractor:
    def __init__(self, handler: RequestHandler):
        self.handler = handler

    def user_id(self, user_id) -> ObjectId:
        try:
            return ObjectId(user_id)
        except:
            self.handler.set_status(412, "invalid param=user_id,user_id=%s" % user_id)
            raise Finish()

    def product_id(self, product_id) -> ObjectId:
        try:
            return ObjectId(product_id)
        except:
            self.handler.set_status(412, "invalid param=product_id,product_id=%s" % product_id)
            raise Finish()


class BodyExtractor:
    def __init__(self, handler: RequestHandler):
        self.handler = handler

    # def body(self) -> dict:
    #     try:
    #         return json_decode(self.handler.request.body.decode("utf-8"))
    #     except:
    #         self.handler.set_status(412)
    #         self.handler.finish(
    #             json_encode(
    #                 {
    #                     "status": "error",
    #                     "message": "invalid body,body=%s" % self.handler.request.body
    #                 }
    #             )
    #         )
    #         raise Finish()

    # def user_id(self):
    #     if "user_id" not in self.body():
    #         self.handler.set_status(412, "missing,[user_id]")
    #         raise Finish()
    #     else:
    #         try:
    #             return ObjectId(self.body()["user_id"])
    #         except InvalidId:
    #             self.handler.set_status(412, "invalid param=user_id,user_id=%s" % self.body()["user_id"])
    #             raise Finish()

    # def product_id(self):
    #     if "product_id" not in self.body():
    #         self.handler.set_status(412, "missing,[product_id]")
    #         raise Finish()
    #     else:
    #         try:
    #             return ObjectId(self.body()["product_id"])
    #         except InvalidId:
    #             self.handler.set_status(412, "invalid param=product_id,product_id=%s" % self.body()["product_id"])
    #             raise Finish()


class Favorite(RequestHandler):
    _path_extractor = None
    _favorite_data = None

    def set_default_headers(self):
        if ADD_CORS_HEADERS:
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')

    def initialize(self):
        self._path_extractor = PathExtractor(self)
        self._favorite_data = FavoriteData()
        self._favorite_data.open_connection()

    @asynchronous
    @engine
    def options(self, *args, **kwargs):
        self.finish()

    @asynchronous
    @engine
    def put(self, user_id, product_id, *args, **kwargs):
        self._favorite_data.insert(
            self._path_extractor.user_id(user_id),
            self._path_extractor.product_id(product_id)
        )

        self.set_status(201)
        self.finish()
