import os
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer

import src.utils as utils
from src.folderReader import FolderReader
from src.file_saver import FileSaver
from src.file_reader import FileReader
from src.trackerFactory import create_tracker

import cv2


class Controller(QObject):

    change_color_index = pyqtSignal(int)
    request_bboxes = pyqtSignal()
    request_and_init_bboxes = pyqtSignal()
    remove_rectangle_signal = pyqtSignal(int)
    update_filename = pyqtSignal(str)
    rectangles_signal = pyqtSignal(list, list, list, list, list, list)
    update_image_folder = pyqtSignal(str)

    def __init__(self, parent=None, extension='.png'):
        super().__init__(parent)
        self.mode = utils.MODE_TRACK
        self.tracker_name = 'default'
        self.trackers = []
        self.current_class = 'default'
        self.current_color_index = 0
        self.class_colors = {}

        self.prev_index_frame = 0
        self.current_index_frame = 0

        self.folder_reader = FolderReader()

        self.image_directory = './imagen'
        self.extension = extension
        self.file_saver = FileSaver(self.image_directory)
        self.file_reader = FileReader()

        # self.filenames = ['out2.png', 'out19.png']
        self.filenames = utils.read_files(self.image_directory, self.extension)
        self.filenames = utils.sort_files(self.filenames)

        # Timer for run button
        self.run_timer = QTimer()


    @pyqtSlot(list, list, list, list, list, list)
    def process_rectangles(self, xs, ys, widths, heights, color_indices, recent_draw):
        self.save_rectangles(self.get_prev_filename(), xs, ys, widths, heights, color_indices)
        if self.mode == utils.MODE_TRACK:
            xs, ys, widths, heights, color_indices, recent_draw = self.update_trackers(recent_draw, xs, ys, widths, heights, color_indices)
            recent_draw = [False for i in recent_draw]
            self.rectangles_signal.emit(xs, ys, widths, heights, color_indices, recent_draw)
        elif self.mode == utils.MODE_RTRACK:
            self.send_saved_bboxes()
        elif self.mode == utils.MODE_COPYBBOX:
            recent_draws = [True for i in recent_draw]
            self.rectangles_signal.emit(xs, ys, widths, heights, color_indices, recent_draws)
        elif self.mode == utils.MODE_EMPTY:
            pass
        elif self.mode == utils.MODE_NOTHING:
            self.send_saved_bboxes()

    @pyqtSlot(int)
    def remove_rectangle_slot(self, index):
        self.remove_rectangle(index)

    def remove_rectangle(self, index):
        if index < len(self.trackers):
            self.trackers.pop(index)

    def update_trackers(self, recent_draws, xs, ys, widths, heights, color_indices):
        xs_out = []
        ys_out = []
        widths_out = []
        heights_out = []
        color_indices_out = []
        curr_draws = []
        trackers_to_remove = []
        prev_image = cv2.imread(self.get_prev_filepath() + self.extension)
        current_image = cv2.imread(self.get_current_filepath() + self.extension)
        for index, (recent_draw, x, y, w, h, color_idx) in enumerate(zip(recent_draws, xs, ys, widths, heights, color_indices)):
            if recent_draw:
                tracker = create_tracker(self.tracker_name)
                tracker.init(prev_image, (x, y, w, h))
                self.trackers.append(tracker)
                ret, bbox = tracker.update(prev_image)
            ret, bbox = self.trackers[index].update(current_image)
            if ret:
                xs_out.append(bbox[0])
                ys_out.append(bbox[1])
                widths_out.append(bbox[2])
                heights_out.append(bbox[3])
                color_indices_out.append(color_idx)
                curr_draws.append(True)
            else:
                trackers_to_remove.append(index)

        for index in trackers_to_remove[::-1]:
            self.remove_rectangle_signal.emit(index)

        return xs_out, ys_out, widths_out, heights_out, color_indices_out, curr_draws

    def send_saved_bboxes(self):
        xs, ys, widths, heights, color_indices = self.file_reader.read_bboxes(self.get_current_filepath())
        self.rectangles_signal.emit(xs, ys, widths, heights, color_indices, [False for i in color_indices])

    def save_rectangles(self, filename, xs, ys, widths, heights, color_indices):
        image = cv2.imread(self.get_prev_filepath() + self.extension)
        h, w = image.shape[:2]
        c = 1
        if len(image.shape) > 2:
            c = image.shape[2]
        self.file_saver.save_bboxes(filename, xs, ys, widths, heights, color_indices, w, h, c)

    @pyqtSlot(str)
    def set_tracker_name(self, tracker_name):
        self.tracker_name = tracker_name

        # Try 1
        for index in range(len(self.trackers))[::-1]:
            self.remove_rectangle_signal.emit(index)
        self.send_saved_bboxes()
        self.request_and_init_bboxes.emit()
        # Try 2
        # self.request_and_init_bboxes.emit()

    @pyqtSlot(str)
    def set_current_class(self, class_name):
        self.current_class = class_name
        self.current_color_index = self.class_colors[self.current_class]
        self.change_color_index.emit(self.current_color_index)

    def update_mode(self, mode):
        self.mode = mode

    @pyqtSlot()
    def update_mode_to_track(self):
        self.update_mode(utils.MODE_TRACK)
        self.set_tracker_name(self.tracker_name)

    @pyqtSlot()
    def update_mode_to_rtrack(self):
        self.update_mode(utils.MODE_RTRACK)

    @pyqtSlot()
    def update_mode_to_copybbox(self):
        self.update_mode(utils.MODE_COPYBBOX)

    @pyqtSlot()
    def update_mode_to_empty(self):
        self.update_mode(utils.MODE_EMPTY)

    @pyqtSlot()
    def update_mode_to_nothing(self):
        self.update_mode(utils.MODE_NOTHING)

    def set_classes(self, items):
        self.class_colors = {color: index for index, color in enumerate(items)}

    @pyqtSlot()
    def request_next(self):
        if self.current_index_frame < len(self.filenames) - 1:
            self.prev_index_frame = self.current_index_frame
            self.current_index_frame += 1
            self.update_filename.emit(self.get_current_frame())
            self.request_bboxes.emit()

    @pyqtSlot()
    def request_prev(self):
        if self.current_index_frame > 0:
            self.prev_index_frame = self.current_index_frame
            self.current_index_frame -= 1
            self.update_filename.emit(self.get_current_frame())
            self.request_bboxes.emit()

    def get_current_frame(self):
        if self.current_index_frame < 0 or self.current_index_frame >= len(self.filenames):
            return None
        else:
            path = os.path.join(self.image_directory, self.filenames[self.current_index_frame])
            return path

    def get_current_filename(self):
        return self.filenames[self.current_index_frame]

    def get_prev_filename(self):
        return self.filenames[self.prev_index_frame]

    def get_current_filepath(self):
        return os.path.join(self.image_directory, self.get_current_filename())

    def get_prev_filepath(self):
        return os.path.join(self.image_directory, self.get_prev_filename())

    def select_folder(self):
        folder = self.folder_reader.get_folder()
        self.image_directory = folder
        self.file_saver.set_folder(folder)
        self.filenames = utils.read_files(self.image_directory, self.extension)
        self.filenames = utils.sort_files(self.filenames)
        self.prev_index_frame = 0
        self.current_index_frame = 0

        for index in range(len(self.trackers))[::-1]:
            self.remove_rectangle_signal.emit(index)

        self.update_filename.emit(self.get_current_frame())
        self.send_saved_bboxes()
        self.request_and_init_bboxes.emit()

        self.update_image_folder.emit(folder)
        print('NEWFOLDER', folder)


    @pyqtSlot()
    def run_tracking(self):
        self.run_timer.start(50)

    @pyqtSlot()
    def stop_tracking(self):
        self.run_timer.stop()