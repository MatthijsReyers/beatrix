from sys import platform
import os

def safe_import_cv():
    """ On Linux PyQt5 will try to use shared libraries built by opencv when opencv is imported, even 
    though they are incompatible and cause a crash. This function imports cv2 and does some environment
    variable magic to fix that. """
    import cv2
    unsafe_build = False
    try:
        from cv2.version import ci_build, headless
        unsafe_build = ci_build and not headless
    finally:
        if platform.startswith("linux") and unsafe_build:
            if 'QT_QPA_PLATFORM_PLUGIN_PATH' in os.environ.keys():
                os.environ.pop('QT_QPA_PLATFORM_PLUGIN_PATH')
            if 'QT_QPA_FONTDIR' in os.environ.keys():
                os.environ.pop('QT_QPA_FONTDIR')
    return cv2