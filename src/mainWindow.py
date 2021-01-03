from PyQt5.QtWidgets import (QMainWindow,
                             QWidget,
                             QPushButton,
                             QRadioButton,
                             QGroupBox,
                             QAction,
                             QShortcut
                             )
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence

from src.imageWidget import ImageWidget
from src.comboBoxWidget import ComboBoxWidget
from src.listWidget import ListWidget

from src.controller import Controller
from src.xmlCreator import XMLCreator
from src.folderReader import FolderReader
import src.utils as utils


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)

        self.extension = '.jpg'

        self.image_width, self.image_height = 1280, 720
        # self.image_width, self.image_height = 640, 360

        # Widget de Imagen.
        self.image_widget = ImageWidget(self.image_width, self.image_height)

        # Widget de seleccion de tracker.
        self.tracker_combobox = ComboBoxWidget('./config/tracker_list.txt')
        self.tracker_groupBox = self.create_groupBox_from_widget('Tracker', self.tracker_combobox)

        # Widget de seleccion de clase.
        self.class_list = ListWidget('./config/class_list.txt')
        self.class_groupBox = self.create_groupBox_from_widget('Classes', self.class_list)

        # Botones de acciones.
        self.radio_track = QRadioButton(utils.MODE_DICT[utils.MODE_TRACK])
        self.radio_rtrack = QRadioButton(utils.MODE_DICT[utils.MODE_RTRACK])
        self.radio_copy = QRadioButton(utils.MODE_DICT[utils.MODE_COPYBBOX])
        self.radio_empty = QRadioButton(utils.MODE_DICT[utils.MODE_EMPTY])
        self.radio_nothing = QRadioButton(utils.MODE_DICT[utils.MODE_NOTHING])
        self.group_box = self.create_button_group()

        # Botones de ejecucion.
        self.button_prev = QPushButton('Prev')
        self.button_next = QPushButton('Next')
        self.button_run = QPushButton('Run')
        self.button_stop = QPushButton('Stop')

        # Folder reader.
        self.folder_reader = FolderReader()
        # Exportar txt a xml.
        self.xml_creator = XMLCreator('./imagen', self.extension)

        # Main controller.
        self.controller = Controller(self, self.extension)
        self.controller.set_classes(self.class_list.get_items())

        # Shortcuts.
        self.shortcut_next = QShortcut(QKeySequence('D'), self)
        self.shortcut_prev = QShortcut(QKeySequence('A'), self)
        self.shortcut_1 = QShortcut(QKeySequence('1'), self)
        self.shortcut_2 = QShortcut(QKeySequence('2'), self)
        self.shortcut_3 = QShortcut(QKeySequence('3'), self)
        self.shortcut_4 = QShortcut(QKeySequence('4'), self)
        self.shortcut_5 = QShortcut(QKeySequence('5'), self)
        self.shortcut_6 = QShortcut(QKeySequence('6'), self)
        self.shortcut_7 = QShortcut(QKeySequence('7'), self)
        self.shortcut_8 = QShortcut(QKeySequence('8'), self)
        self.shortcut_9 = QShortcut(QKeySequence('9'), self)

        self.setup_ui()

        self.setup_signals()

    def setup_signals(self):
        # Mode signals.
        self.radio_track.clicked.connect(self.controller.update_mode_to_track)
        self.radio_rtrack.clicked.connect(self.controller.update_mode_to_rtrack)
        self.radio_copy.clicked.connect(self.controller.update_mode_to_copybbox)
        self.radio_empty.clicked.connect(self.controller.update_mode_to_empty)
        self.radio_nothing.clicked.connect(self.controller.update_mode_to_nothing)

        # Class selection signals.
        self.class_list.currentTextChanged.connect(self.controller.set_current_class)
        self.controller.change_color_index.connect(self.image_widget.update_current_color_index)

        # Tracker selection signals.
        self.tracker_combobox.currentTextChanged.connect(self.controller.set_tracker_name)

        # Get BBoxes.
        self.button_next.clicked.connect(self.controller.request_next)
        self.button_prev.clicked.connect(self.controller.request_prev)
        self.button_run.clicked.connect(self.controller.run_tracking)
        self.button_stop.clicked.connect(self.controller.stop_tracking)
        self.controller.request_bboxes.connect(self.image_widget.emit_rectangles)
        self.controller.request_and_init_bboxes.connect(self.image_widget.emit_rectangles_and_init)
        self.image_widget.rectangles_signal.connect(self.controller.process_rectangles)

        # Update image.
        self.controller.update_filename.connect(self.image_widget.set_image_file)

        # Update bboxes.
        self.controller.rectangles_signal.connect(self.image_widget.receive_rectangles)

        # Remove bbox.
        self.controller.remove_rectangle_signal.connect(self.image_widget.remove_rectangle_slot)
        self.image_widget.rectangle_removed_signal.connect(self.controller.remove_rectangle_slot)

        # Run button timer
        self.controller.run_timer.timeout.connect(self.controller.request_next)

        # Folder change
        self.controller.update_image_folder.connect(self.select_folder)

        # Shortcuts
        self.shortcut_next.activated.connect(self.controller.request_next)
        self.shortcut_prev.activated.connect(self.controller.request_prev)
        self.shortcut_1.activated.connect(self.class_list.set_row_1)
        self.shortcut_2.activated.connect(self.class_list.set_row_2)
        self.shortcut_3.activated.connect(self.class_list.set_row_3)
        self.shortcut_4.activated.connect(self.class_list.set_row_4)
        self.shortcut_5.activated.connect(self.class_list.set_row_5)
        self.shortcut_6.activated.connect(self.class_list.set_row_6)
        self.shortcut_7.activated.connect(self.class_list.set_row_7)
        self.shortcut_8.activated.connect(self.class_list.set_row_8)
        self.shortcut_9.activated.connect(self.class_list.set_row_9)

        # Set mode
        self.radio_track.click()
        # Set current class
        self.controller.set_current_class(self.class_list.currentItem().text())
        # Initialize first image
        self.image_widget.set_image_file(self.controller.get_current_frame())
        # Update bbox if saved
        self.controller.send_saved_bboxes()
        # Update tracker name
        self.controller.set_tracker_name(self.tracker_combobox.currentText())

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout()

        option_widget_layout = QVBoxLayout()

        option_widget_layout.addWidget(self.group_box)
        option_widget_layout.addWidget(self.tracker_groupBox)
        option_widget_layout.addWidget(self.class_groupBox)

        grid_button_layout = QGridLayout()
        grid_button_layout.addWidget(self.button_prev, 0, 0)
        grid_button_layout.addWidget(self.button_next, 0, 1)
        grid_button_layout.addWidget(self.button_run, 1, 0)
        grid_button_layout.addWidget(self.button_stop, 1, 1)
        option_widget_layout.addLayout(grid_button_layout)

        main_layout.addWidget(self.image_widget)
        main_layout.addLayout(option_widget_layout)

        self.centralWidget().setLayout(main_layout)

        # Menubar
        folder_action = QAction('Select Folder', self)
        folder_action.triggered.connect(self.controller.select_folder)
        export_action = QAction('Export', self)
        export_action.triggered.connect(self.xml_creator.export_txt_to_xml)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(folder_action)
        file_menu.addAction(export_action)

        self.statusBar().showMessage('')

    def create_button_group(self):
        group_box = QGroupBox('Modo')
        self.radio_track.setChecked(True)
        vbox = QVBoxLayout()
        vbox.addWidget(self.radio_track)
        vbox.addWidget(self.radio_rtrack)
        vbox.addWidget(self.radio_copy)
        vbox.addWidget(self.radio_empty)
        vbox.addWidget(self.radio_nothing)
        vbox.addStretch(1)
        group_box.setLayout(vbox)
        return group_box

    def create_groupBox_from_widget(self, name, widget):
        group_box = QGroupBox(name)
        vbox = QVBoxLayout()
        vbox.addWidget(widget)
        group_box.setLayout(vbox)
        return group_box


    @pyqtSlot(str)
    def select_folder(self, folder):
        self.xml_creator.set_folder_path(folder)


