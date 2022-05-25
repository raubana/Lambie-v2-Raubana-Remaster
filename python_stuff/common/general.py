import time

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