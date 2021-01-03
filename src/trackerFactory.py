import cv2


OPENCV_OBJECT_TRACKERS = {'default': cv2.TrackerKCF_create,
                          'csrt': cv2.TrackerCSRT_create,
                          'kcf': cv2.TrackerKCF_create,
                          'boosting': cv2.TrackerBoosting_create,
                          'mil': cv2.TrackerMIL_create,
                          'tld': cv2.TrackerTLD_create,
                          'medianflow': cv2.TrackerMedianFlow_create,
                          'mosse': cv2.TrackerMOSSE_create
                          }


def create_tracker(name):
    tracker = OPENCV_OBJECT_TRACKERS[name]
    # return cv2.TrackerKCF_create()
    return tracker()


class TrackerFactory:

    def __init__(self):
        pass
