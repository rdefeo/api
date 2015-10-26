from api.settings import TILE_IMAGE_PATH
from slugify import slugify

__author__ = 'robdefeo'


class Suggestions:
    def __init__(self, product_content, brand_slug_cache):
        self._product_content = product_content
        self._brand_slug_cache = brand_slug_cache
        from basehash import base62
        self.base62hash = base62(length=4)

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
                        "url": self.create_url(product)
                    }
                )
                items.append(product)
        return items

    def create_url(self, product):
        geo = "uk"
        brand = next(
            (x["_id"]["key"] for x in product["attributes"] if x["_id"]["type"] == "brand"),
            None
        )
        if brand is not None:
            brand_slug = self._brand_slug_cache.get(brand)
        else:
            brand_slug = None

        title_slug_stopwords = brand_slug.split("-") if brand_slug is not None else []
        title_slug = next(
            (slugify(
                x["_id"]["value"],
                save_order=True,
                max_length=50,
                word_boundary=True,
                stopwords=title_slug_stopwords
            ) for x in product["attributes"] if x["_id"]["type"] == "title"),
            ''
        )
        # TODO this can be removed pretty soon
        if "sequence" in product:
            if isinstance(product["sequence"],int):
                sequence = product["sequence"]
            else:
                sequence = None
        else:
            sequence = None
            
        if sequence is not None and brand_slug is not None and title_slug is not '':
            return "/%s/%s/%s~%s/" % (
                geo,
                slugify(brand, save_order=True),
                title_slug,
                sequence
            )
        else:
            return "/%s/detail/%s/" % (geo, str(product["_id"]))

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
