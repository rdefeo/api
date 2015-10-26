from datetime import datetime, timedelta
from tornado.log import app_log
from api.cache.base import Base
from prproc.data import AttributeData
__author__ = 'robdefeo'


class BrandSlug(Base):
    attribute_data = None

    def initialize(self):
        self.attribute_data = AttributeData()
        self.attribute_data.open_connection()

    def _get_from_service(self, key):
        try:
            brand = self.attribute_data.get_by(_id_type="brand",_id_key=key)
            if brand is not None:
                return brand["slug"] if "slug" in brand else None
            else:
                return None
        except:
            app_log.error("get brand from database,key=%s", key)
            return None