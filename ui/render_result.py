from typing import Tuple, List

from PIL import Image

BoundingBox = Tuple[int, int, int, int]


class RenderResult:
    def __init__(self, image: Image) -> None:
        self._image = image
        self._bbs = []

    def add_bounding_box(self, bb: BoundingBox) -> None:
        self._bbs.append(bb)

    @property
    def image(self) -> Image:
        return self._image

    @property
    def bounding_boxes(self) -> List[BoundingBox]:
        return self._bbs
