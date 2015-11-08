from tornado.log import app_log

from api.cache.base import Base
from user.data import FavoriteData


class Favorites(Base):
    _favorite_data = None

    def initialize(self):
        self._favorite_data = FavoriteData()
        self._favorite_data.open_connection()

    def _get_from_service(self, _id):
        try:
            app_log.debug("Favorites,get_from_service,_id=%s", _id)
            favorites = self._favorite_data.find(_id)
            return [str(x["_id"]["product_id"]) for x in favorites]

        except:
            app_log.error("get_from_service,_id=%s", _id)
            return None
