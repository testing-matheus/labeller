import os


class FileSaver:

    def __init__(self, folder):
        self.folder = folder

    def set_folder(self, folder):
        self.folder = folder

    def save_bboxes(self, name, xs, ys, widths, heights, classes, width, height, channels):
        filepath = os.path.join(self.folder, name + '.txt')
        with open(filepath, 'w') as file:
            for x, y, w, h, class_idx in zip(xs, ys, widths, heights, classes):
                file.write(f'%i,%i,%i,%i,%i,%i,%i,%i\n' % (x, y, w, h, class_idx, width, height, channels))
