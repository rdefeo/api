from bson import ObjectId


class User:
    def __init__(self, user_info_cache):
        self.user_info = user_info_cache

    def get_profile_picture(self, _id: ObjectId):
        user_info = self.user_info.get(_id)
        if user_info is not None and "profile_photo_url" in user_info:
            return user_info["profile_photo_url"]
        else:
            return None

    def get_favorites(self):
        # TODO its own seperate logic i think?????
        pass
