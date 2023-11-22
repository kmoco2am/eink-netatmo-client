from PIL import ImageDraw


class WidgetBase:
    def __init__(self, width: int, height: int):
        self._height = height
        self._width = width
        self._top = 0
        self._left = 0
        self._abs_top = 0
        self._abs_left = 0
        self._children = []
        self._draw_border = False
        self._children_draw_border = False
        self._background = 255
        self._foreground = 0

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, top: int):
        self._top = top
        return self

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, left: int):
        self._left = left
        return self

    @property
    def abs_top(self):
        return self._abs_top

    @abs_top.setter
    def abs_top(self, abs_top):
        self._abs_top = abs_top
        for child in self._children:
            child.abs_top = abs_top + child.top

    @property
    def abs_left(self):
        return self._abs_left

    @abs_left.setter
    def abs_left(self, abs_left):
        self._abs_left = abs_left
        for child in self._children:
            child.abs_left = abs_left + child.left

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, background):
        self._background = background

    @property
    def foreground(self):
        return self._foreground

    @foreground.setter
    def foreground(self, foreground):
        self._foreground = foreground

    def is_draw_border(self, draw_border: bool):
        self._draw_border = draw_border

    def is_children_draw_border(self, children_draw_border: bool = False):
        for child in self._children:
            child.is_draw_border(children_draw_border)
            child.is_children_draw_border(children_draw_border)

    def draw(self, draw: ImageDraw):
        if self._draw_border:
            draw.rectangle((self.abs_left, self.abs_top,
                            self.abs_left + self.width - 1,
                            self.abs_top + self.height - 1),
                           outline=self.foreground, fill=self.background)

    def add_child(self, child):
        self._children.append(child)
        child.abs_left = self.abs_left + child.left
        child.abs_top = self.abs_top + child.top
