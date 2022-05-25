import notifications.constants
import notifications.NotificationHandler


def init():
    notifications.constants.HANDLER = notifications.NotificationHandler.NotificationHandler()
    notifications.constants.HANDLER.start()


def quit():
    notifications.constants.HANDLER.end()