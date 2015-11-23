from tornado.escape import json_decode
from bson.json_util import loads


class MessageHandler:
    @staticmethod
    def json_decode(body):
        return json_decode(body)

    @staticmethod
    def bson_json_decode_and_load(body):
        return loads(body.decode("utf-8"))

