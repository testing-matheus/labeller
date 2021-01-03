import os
from src.utils import read_files, sort_files
from src.file_reader import FileReader
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QFileDialog

# Leer archivo txt y obtener valores
def get_values(file_path):

    # Inicializar lista con valores
    value_list = []

    # Abrir archivo
    with open(file_path,'r') as fp:

        # Leer cada linea
        for line in fp:

            # Eliminar '\n' en linea y separar numeros entre ','
            line = line.strip('\n').split(',')
            
            # Transformar numeros en string a enteros en una lista
            intmap = map(int,line)
            intlist = list(intmap)

            # Almacenar datos
            value_list.append(intlist)

    return value_list


# Escribir archivo XML
def write_XML(folder_name, file_name, path, value_list, new_xml_file):

    # Crear y abrir archivo
    with open(new_xml_file,'w') as fp:
        # Leer template inicial, reemplazar y escribir
        with open('./config/template_ini.xml','r') as fp_template:
            content_org = fp_template.read()
            content_new = content_org.replace('folder_var',folder_name)
            content_new = content_new.replace('filename_var',file_name)
            content_new = content_new.replace('path_var',path)
            print('VALULUS', value_list)
            content_new = content_new.replace('image_width', str(value_list[0][5]))
            content_new = content_new.replace('image_height', str(value_list[0][6]))
            content_new = content_new.replace('image_depth', str(value_list[0][7]))
            fp.write(content_new)

        # Leer template de objects, reemplazar y escribir
        with open('./config/template_obj.xml','r') as fp_template:

            content_org = fp_template.read()
            
            for values in value_list:
                content_new = content_org.replace('xmin_var',str(values[0]))
                content_new = content_new.replace('ymin_var',str(values[1]))
                content_new = content_new.replace('xmax_var',str(values[2]))
                content_new = content_new.replace('ymax_var',str(values[3]))
                content_new = content_new.replace('class_var',str(values[4]))
                fp.write(content_new)                

        # Leer template final, reemplazar y escribir
        with open('./config/template_end.xml','r') as fp_template:
            content_org = fp_template.read()
            fp.write(content_org)

"""
matrix = get_values('imagen52.png.txt')
image_shape = (1920, 1080, 3)
write_XML('detector_camiones',
          '52.jpg',
          '/home/anilitica/Desktop/detector_camiones/images/52.jpg',
          matrix,
          image_shape,
          '52.xml')
"""


class XMLCreator:

    def __init__(self, folder_path='', image_extension='.jpg'):
        self.folder_path = os.path.expanduser(folder_path)
        self.image_extension = image_extension
        self.extension = '.txt'

    def set_folder_path(self, folder_path):
        self.folder_path = os.path.expanduser(folder_path)

    def export_txt_to_xml(self):
        items = self.get_list()
        for base_name in items:
            print('MATRIX PATH', os.path.join(self.folder_path, base_name + self.extension))
            matrix = get_values(os.path.join(self.folder_path, base_name + self.extension))
            write_XML(self.folder_path,
                      base_name + self.image_extension,
                      os.path.join(self.folder_path, base_name + self.image_extension),
                      matrix,
                      os.path.join(self.folder_path, base_name + '.xml'))

    @pyqtSlot(str)
    def update_image_folder(self, folder):
        self.set_folder_path(folder)

    def get_list(self):
        items = read_files(self.folder_path, self.extension)
        items = sort_files(items)
        return items
