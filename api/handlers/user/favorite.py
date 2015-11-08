from bson import ObjectId
from tornado.gen import engine
from tornado.web import RequestHandler, asynchronous, Finish
from bson.json_util import dumps

from user.data import FavoriteData
from user import __version__
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

    @asynchronous
    @engine
    def delete(self, user_id, product_id, *args, **kwargs):
        self._favorite_data.delete(
            self._path_extractor.user_id(user_id),
            self._path_extractor.product_id(product_id)
        )

        self.set_status(204)
        self.finish()


    @asynchronous
    @engine
    def get(self, user_id, product_id, *args, **kwargs):
        favorite_record = self._favorite_data.get(
            self._path_extractor.user_id(user_id),
            self._path_extractor.product_id(product_id)
        )

        self.set_status(201)
        self.finish(
            dumps(
                {
                    "favorited": favorite_record is not None
                }
            )
        )

class Favorites(RequestHandler):
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
    def get(self, user_id, *args, **kwargs):
        favorites = self._favorite_data.find(
            self._path_extractor.user_id(user_id)
        )

        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.finish(
            dumps(
                {
                    "favorites": [
                        x["_id"]["product_id"]
                        for x in favorites
                        ],
                    "version": __version__
                }
            )
        )
