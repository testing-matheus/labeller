import os


class FileReader:

    def __init__(self):
        pass

    def read_bboxes(self, filepath):
        xs = []
        ys = []
        widths = []
        heights = []
        classes = []
        filepath = filepath + '.txt'
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                for line in file.readlines():
                    x, y, w, h, class_idx, width, height, channels = line.split(',')
                    xs.append(int(x))
                    ys.append(int(y))
                    widths.append(int(w))
                    heights.append(int(h))
                    classes.append(int(class_idx))
        return xs, ys, widths, heights, classes

    """
    def save_bboxes(self, name, xs, ys, widths, heights, classes):
        filepath = os.path.join(self.folder, name + '.txt')
        with open(filepath, 'w') as file:
            for x, y, w, h, class_idx in zip(xs, ys, widths, heights, classes):
                file.write(f'%i,%i,%i,%i,%i\n' % (x, y, w, h, class_idx))
    """