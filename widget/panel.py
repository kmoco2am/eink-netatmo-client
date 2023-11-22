from PIL import ImageDraw

from widget.widget_base import WidgetBase


class PanelWidget(WidgetBase):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)

    def draw(self, draw: ImageDraw):
        super().draw(draw)
        for child in self._children:
            child.draw(draw)

