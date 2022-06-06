import os
import time

import bpy

import constants


def safe_print(*args, **kwargs):
    constants.other.PRINT_LOCK.acquire()
    print(*args, **kwargs)
    constants.other.PRINT_LOCK.release()


# For ensuring we pass things by reference.
class Holder(object):
    def __init__(self, held):
        self.held = held


class ProgressPrinter(object):
    def __init__(self, total, freq=5, verbose_level=4):
        self.total = total
        self.freq = freq
        self.verbose_level = verbose_level

        self.last_percent = 0.0
        self.last_time = time.time()

    def update(self, current):
        if constants.other.VERBOSE_LEVEL >= self.verbose_level:
            this_time = time.time()
            this_percent = current / self.total
            if this_time - self.last_time >= self.freq:
                self.last_time = this_time
                self.last_percent = this_percent
                safe_print(" " + ("-" * self.verbose_level) + " " + str(round(100 * this_percent, 2)) + "%")


def safely_delete_file(filepath):
    safe_extensions = ( ".txt", ".png" )

    filepath = bpy.path.native_pathsep(filepath)
    filepath = os.path.normpath(filepath)

    if os.path.isfile(filepath):
        path, ext = os.path.splitext(filepath)

        if ext in safe_extensions:
            safe_print("Deleting file:", filepath)
            os.remove(filepath)
        else:
            raise Exception("Whoa, whoa! I can't delete that file! "+filepath)
    else:
        safe_print("Attempted to delete file but it did not exist:", filepath)
