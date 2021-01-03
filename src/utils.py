from PyQt5.QtCore import Qt
import os
import re


MODE_TRACK = 1
MODE_RTRACK = 2
MODE_COPYBBOX = 3
MODE_EMPTY = 4
MODE_NOTHING = 5

MODE_DICT = {MODE_TRACK: 'Track',
             MODE_RTRACK: 'Reverse track',
             MODE_COPYBBOX: 'Copy BBox',
             MODE_EMPTY: 'Empty BBox',
             MODE_NOTHING: 'Do Nothing'}

COLORS = [Qt.white,
          Qt.red,
          Qt.green,
          Qt.blue,
          Qt.cyan,
          Qt.magenta,
          Qt.yellow,
          Qt.gray]


def read_files(directory, extension):
    files = os.listdir(directory)
    return [file[:-len(extension)] for file in files if file.endswith(extension)]


def sort_files(files):
    files.sort(key=natural_keys)
    return files


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r'(\d+)', text)]



