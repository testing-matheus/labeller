from PyQt5.QtWidgets import QFileDialog
from src.utils import read_files, sort_files


class FolderReader:

    def __init__(self):
        pass

    def get_folder(self):
        folder = QFileDialog.getExistingDirectory(None,
                                                  'Seleccione carpeta con imagenes',
                                                  '.')
        items = read_files(folder, '.jpg')
        items = sort_files(items)
        return folder
