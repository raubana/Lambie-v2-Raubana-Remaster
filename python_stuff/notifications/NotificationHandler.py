import time
import datetime
import requests
import threading

import notifications.constants

import common


class NotificationHandler(object):
    def __init__(self):
        if not notifications.constants.TELEGRAM_YOURID or not notifications.constants.TELEGRAM_BOTTOKEN:
            raise Exception("Notification System is enabled but not setup. Please set ID and Bot Token in constants.")

        self.running = False
        self.failed = False
        self.access_lock = None
        self.next_notification = None
        self.next_notification_is_silent = True
        self.last_notification_time = time.time()
        self.last_queued_time = time.time()

        self.thread = None

    """
    def __del__(self):
        # I hope this works as intended... EDIT: IT DOES NOT.
        print( multiprocessing.parent_process(), threading.main_thread().ident, threading.get_ident() )
        #if multiprocessing.parent_process() is None and threading.main_thread().ident == threading.get_ident():
        self.end()
    """

    def add_notification(self, message, is_silent=True, add_datetime=True, prelocked=False):
        if not notifications.constants.ENABLED:
            return

        if not prelocked: self.access_lock.acquire()

        if self.failed:
            common.general.safe_print("NOTIFICATION SYSTEM: add_notification called after failure. ignored.")
            if not prelocked: self.access_lock.release()
            return

        new_message = str(message)
        if add_datetime:
            new_message += "\n" + str(datetime.datetime.now())

        if self.next_notification is not None:
            self.next_notification = self.next_notification + "\n--------------------------------------\n" + new_message
        else:
            self.next_notification = new_message

        self.last_queued_time = time.time()

        self.next_notification_is_silent = self.next_notification_is_silent and is_silent

        if not prelocked: self.access_lock.release()

    def _send_notification(self):
        if not notifications.constants.ENABLED:
            return

        self.access_lock.acquire()

        if self.next_notification is not None:
            send_conditions_met = False

            if self.running:
                t = time.time()

                if t > self.last_queued_time + notifications.constants.DELAY:
                    if self.next_notification_is_silent:
                        if t > self.last_notification_time + notifications.constants.FREQ_SILENT:
                            send_conditions_met = True
                    else:
                        if t > self.last_notification_time + notifications.constants.FREQ:
                            send_conditions_met = True
            else:
                send_conditions_met = True

            if send_conditions_met:
                if self.failed:
                    common.general.safe_print("NOTIFICATION SYSTEM: _send_notification called after failure. will not attempt sending.")
                else:
                    url = "https://api.telegram.org/bot" + notifications.constants.TELEGRAM_BOTTOKEN + "/sendMessage"
                    params = {}
                    if self.next_notification_is_silent: params["disable_notification"] = "true"
                    params["chat_id"] = notifications.constants.TELEGRAM_YOURID
                    params["text"] = self.next_notification

                    r = requests.get(url, params=params)

                    if not (r.status_code == requests.codes.ok):
                        self.failed = True
                        self.running = False
                        common.general.safe_print("")
                        common.general.safe_print("!!! NOTIFICATION SYSTEM FAILURE !!!")
                        common.general.safe_print("STATUS CODE:", r.status_code)
                        common.general.safe_print("NOTIFICATION SYSTEM DISABLED")
                        common.general.safe_print("")

                self.last_notification_time = time.time()
                self.next_notification = None
                self.next_notification_is_silent = True

        self.access_lock.release()

    def __main(self):
        while True:
            time.sleep(1)

            if notifications.constants.REMINDERS:
                self.access_lock.acquire()
                if self.next_notification is None and time.time() - self.last_notification_time >= notifications.constants.REMINDERFREQ:
                    self.add_notification(" ... \u23f0 still running ... ", add_datetime=False, prelocked=True)
                self.access_lock.release()

            self._send_notification()

            if not self.running:
                common.general.safe_print("NOTIFICATION SYSTEM: thread noted running is false. thread terminating self.")
                break

    def start(self):
        if self.access_lock is not None: self.access_lock.acquire()
        if self.thread is not None:
            self.running = False
            while self.thread.is_alive():
                common.general.safe_print("NOTIFICATION SYSTEM: waiting for existing thread to die.")
                time.sleep(0.5)
        if self.access_lock is not None: self.access_lock.release()

        self.access_lock = threading.Lock()

        self.access_lock.acquire()

        self.running = True
        self.failed = False
        self.next_notification = None
        self.next_notification_is_silent = True
        self.last_notification_time = time.time()
        self.last_queued_time = time.time()

        self.thread = threading.Thread(target=self.__main)
        self.thread.start()

        self.access_lock.release()

    def end(self):
        common.general.safe_print("NOTIFICATION SYSTEM: ending...")

        self.access_lock.acquire()

        if not self.running:
            common.general.safe_print("NOTIFICATION SYSTEM: already ended. ignoring.")
        else:
            self.running = False

            self.access_lock.release()

            while self.thread is not None and self.thread.is_alive():
                common.general.safe_print("NOTIFICATION SYSTEM: waiting for thread to die.")
                time.sleep(0.5)

            while self.next_notification is not None and not self.failed:
                common.general.safe_print("NOTIFICATION SYSTEM: attempting to send last notification before end.")
                self._send_notification()

        common.general.safe_print("NOTIFICATION SYSTEM: end finished.")
