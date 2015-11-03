from tornado.log import app_log

from api.cache.base import Base
from user.data import UserData


class UserInfo(Base):
    _user_data = None

    def initialize(self):
        self._user_data = UserData()
        self._user_data.open_connection()

    def _get_from_service(self, _id):
        try:
            app_log.debug("UserInfo,get_from_service,_id=%s", _id)
            user_info = self._user_data.get(_id)
            data = {}
            if user_info is not None and "facebook_user_data" in user_info and "picture" in user_info[
                "facebook_user_data"] and "data" in user_info["facebook_user_data"]["picture"] and "url" in \
                    user_info["facebook_user_data"]["picture"]["data"]:

                data["profile_photo_url"] = user_info["facebook_user_data"]["picture"]["data"]["url"]

                return data
            else:
                return None

        except:
            app_log.error("get_from_service,_id=%s", _id)
            return None
