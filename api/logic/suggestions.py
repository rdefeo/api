from api.settings import TILE_IMAGE_PATH
from slugify import slugify
from prproc.url import create_product_url
__author__ = 'robdefeo'


class Suggestions:
    def __init__(self, product_content):
        self._product_content = product_content

    def fill(self, suggestions):
        items = []
        for suggestion in suggestions:
            product = self._product_content.get(suggestion["_id"])
            if product is not None:
                product.update(
                    {
                        "tile": self.get_tile(product),
                        "score": suggestion["score"],
                        "reasons": suggestion["reasons"],
                        "_id": str(product["_id"]),
                        "position": suggestion["index"],
                        "url": create_product_url(product)
                    }
                )
                items.append(product)
        return items

    def get_tile(self, suggestion):
        for image in suggestion["images"]:
            if "tiles" in image:
                for tile in image["tiles"]:
                    if "width" in image and "height" in image:
                        image_scale = "width" if image["width"] > image["height"]  else "height"
                    else:
                        image_scale = "width"
                    if tile["w"] == "w-md":
                        return {
                            "image_scale": image_scale,
                            "colspan": 1,
                            "rowspan": 1 if tile["h"] == "h-md" else 2,
                            "image_url": "%s%s" % (TILE_IMAGE_PATH, tile["path"])
                        }
