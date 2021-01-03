from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush
import PyQt5.QtCore
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from src.utils import COLORS
from src.file_reader import FileReader


def apply_abs_rectangle(x0, y0, width, height):
    if width < 0:
        x0 = x0 + width
        width = -width
    if height < 0:
        y0 = y0 + height
        height = -height

    return x0, y0, width, height


def draw_rectangle(painter, x, y, w, h, color):
    painter.setPen(QPen(color, 2, Qt.SolidLine))
    painter.setBrush(QBrush(color, Qt.NoBrush))
    painter.drawRect(x, y, w, h)
    painter.setBrush(QBrush(color, Qt.SolidPattern))
    painter.drawEllipse(x + w / 2, y + h / 2, 5, 5)


def scale_points(factors, xs, ys, widths, heights):
    x_factor, y_factor = factors
    xpos = [x0 * x_factor for x0 in xs]
    ypos = [y0 * y_factor for y0 in ys]
    ws = [w * x_factor for w in widths]
    hs = [h * y_factor for h in heights]

    return (xpos, ypos, ws, hs)


class ImageWidget(QLabel):

    rectangles_signal = pyqtSignal(list, list, list, list, list, list)
    rectangle_removed_signal = pyqtSignal(int)

    def __init__(self, width=1280, height=720, parent=None):
        QLabel.__init__(self, parent)
        self.xpos = []
        self.ypos = []
        self.widths = []
        self.heights = []
        self.rect_centers = []
        self.color_indices = []
        self.recent_draw = []  # Flag to indicate if bbox was created now.
        self.image_width = width
        self.image_height = height

        self.image = QPixmap(self.image_width, self.image_height)
        self.original_size = self.image.size()
        self.scaled_image = QPixmap()
        self.original_scaled_image = self.scaled_image.copy()
        self.scaled_image_to_draw = self.scaled_image.copy()
        self.setFixedSize(self.scaled_image.size())

        self.current_color_index = 0

        self.update_pixmap(self.image)

        self.drawing = False
        self.last_point = None

        self.file_reader = FileReader()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.scaled_image)

    def mousePressEvent(self, event):
        # Draw
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.pos1 = event.pos()
        # Delete
        if event.button() == Qt.RightButton:
            x, y = event.pos().x(), event.pos().y()
            min_error = 100000
            min_idx = -1
            for index, (center_x, center_y) in enumerate(self.rect_centers):
                error = (x - center_x)**2 + (y - center_y)**2
                if error < min_error:
                    min_error = error
                    min_idx = index
            if min_error < 20**2:
                self.remove_rectangle(min_idx)
                self.draw_all_rectangles()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton and self.drawing:
            # Image without previous rectangles
            self.scaled_image = self.scaled_image_to_draw.copy()
            # Painter
            painter = QPainter(self.scaled_image)
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            # Rectangle params
            width = event.pos().x() - self.pos1.x()
            height = event.pos().y() - self.pos1.y()

            painter.drawRect(self.pos1.x(), self.pos1.y(), width, height)

            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            width = event.pos().x() - self.pos1.x()
            height = event.pos().y() - self.pos1.y()

            x, y, w, h = apply_abs_rectangle(self.pos1.x(), self.pos1.y(), width, height)

            self.xpos.append(x)
            self.ypos.append(y)
            self.widths.append(w)
            self.heights.append(h)
            self.rect_centers.append([x + w/2, y + h/2])
            self.color_indices.append(self.current_color_index)
            self.recent_draw.append(True)
            color = COLORS[self.current_color_index % len(COLORS)]

            painter = QPainter(self.scaled_image)
            draw_rectangle(painter, x, y, w, h, color)

            self.update()

            self.scaled_image_to_draw = self.scaled_image.copy()
            self.drawing = False

    @pyqtSlot(str)
    def set_image_file(self, image_filename):
        if image_filename is not None:
            self.image = QPixmap(image_filename)

            self.update_pixmap(self.image)

    def update_pixmap(self, image):
        self.original_size = image.size()
        self.scaled_image = image.scaled(self.image_width, self.image_height, PyQt5.QtCore.Qt.KeepAspectRatio)
        self.original_scaled_image = self.scaled_image.copy()
        self.scaled_image_to_draw = self.original_scaled_image.copy()
        self.setPixmap(self.scaled_image)
        self.setFixedSize(self.scaled_image.size())

    @pyqtSlot()
    def emit_rectangles(self):
        x_factor = self.original_size.width() / self.image_width
        y_factor = self.original_size.height() / self.image_height

        xpos, ypos, widths, heights = scale_points((x_factor, y_factor),
                                                   self.xpos, self.ypos, self.widths, self.heights)
        self.rectangles_signal.emit(xpos, ypos, widths, heights, self.color_indices, self.recent_draw)

    @pyqtSlot()
    def emit_rectangles_and_init(self):
        x_factor = self.original_size.width() / self.image_width
        y_factor = self.original_size.height() / self.image_height

        xpos, ypos, widths, heights = scale_points((x_factor, y_factor),
                                                   self.xpos, self.ypos, self.widths, self.heights)
        for index in range(len(self.recent_draw))[::-1]:
            self.recent_draw[index] = True
            self.rectangle_removed_signal.emit(index)
        self.rectangles_signal.emit(xpos, ypos, widths, heights, self.color_indices, self.recent_draw)

    @pyqtSlot(list, list, list, list, list, list)
    def receive_rectangles(self, xs, ys, widths, heights, color_indices, recent_draw):
        self.clear_rectangles()
        bboxes = (xs, ys, widths, heights, color_indices)
        self.recent_draw = recent_draw
        self.update_bboxes(bboxes)
        self.draw_all_rectangles()

    def clear_rectangles(self):
        self.xpos.clear()
        self.ypos.clear()
        self.widths.clear()
        self.heights.clear()
        self.rect_centers.clear()
        self.color_indices.clear()
        self.recent_draw.clear()

    def remove_rectangle(self, index):
        self.xpos.pop(index)
        self.ypos.pop(index)
        self.widths.pop(index)
        self.heights.pop(index)
        self.rect_centers.pop(index)
        self.color_indices.pop(index)
        self.recent_draw.pop(index)
        self.rectangle_removed_signal.emit(index)

    @pyqtSlot(int)
    def remove_rectangle_slot(self, index):
        self.remove_rectangle(index)

    def draw_all_rectangles(self):
        self.scaled_image_to_draw = self.original_scaled_image.copy()
        self.scaled_image = self.scaled_image_to_draw.copy()
        painter = QPainter(self.scaled_image)
        for x, y, w, h, color_index in zip(self.xpos, self.ypos, self.widths, self.heights, self.color_indices):
            draw_rectangle(painter, x, y, w, h, COLORS[color_index % len(COLORS)])

        self.update()
        self.scaled_image_to_draw = self.scaled_image.copy()

    @pyqtSlot(int)
    def update_current_color_index(self, color_index):
        self.current_color_index = color_index

    def update_bboxes(self, bboxes):
        x_factor = self.image_width / self.original_size.width()
        y_factor = self.image_height / self.original_size.height()
        self.xpos, self.ypos, self.widths, self.heights = scale_points((x_factor, y_factor),
                                                                       bboxes[0], bboxes[1], bboxes[2], bboxes[3])
        self.color_indices = bboxes[4]
        self.rect_centers = [[x + w/2, y + h/2] for  x, y, w, h in zip(self.xpos, self.ypos, self.widths, self.heights)]


