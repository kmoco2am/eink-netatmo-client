from PIL import ImageDraw, ImageFont

from widget.alignments import Alignments
from widget.widget_base import WidgetBase


class TextWidget(WidgetBase):
    def __init__(self, width: int, height: int, font: ImageFont = None):
        super().__init__(width, height)
        self._text = ''
        self._font = font
        self._vertical_align = Alignments.CENTER
        self._horizontal_align = Alignments.CENTER

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text

    @property
    def vertical_alignment(self):
        return self._vertical_align

    @vertical_alignment.setter
    def vertical_alignment(self, vertical_alignment):
        self._vertical_align = vertical_alignment

    @property
    def horizontal_alignment(self):
        return self._horizontal_align

    @horizontal_alignment.setter
    def horizontal_alignment(self, horizontal_alignment):
        self._horizontal_align = horizontal_alignment

    def draw(self, draw: ImageDraw):
        super().draw(draw)
        left, top, right, bottom = draw.textbbox((0,0), self._text, font=self._font)
        font_w = right - left
        font_h = top - bottom
        if font_h <= self.height and font_w <= self.width:
            left_offset = self.abs_left
            if self._horizontal_align == Alignments.CENTER:
                left_offset += (self.width - font_w) // 2
            elif self._horizontal_align == Alignments.RIGHT:
                left_offset += self.width - font_w
            top_offset = self.abs_top
            if self._vertical_align == Alignments.CENTER:
                top_offset += (self.height - font_h) // 2 - 1
            elif self._vertical_align == Alignments.BOTTOM:
                top_offset += self.height - font_h
            draw.text((left_offset, top_offset), self.text,
                      fill=self.foreground, font=self._font)
