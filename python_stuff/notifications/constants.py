ENABLED = False

DELAY = 2  # Delay sending notification(s) for X seconds. Timer resets when a notification is queued.
FREQ = 15  # Send notification(s) every X seconds. Timer resets when a notification is sent.
FREQ_SILENT = 60*3  # Send silent notification(s) every X seconds. Timer resets when a notification is sent.
REMINDERS = True  # Remind me that the script/process is still running every once in a while.
REMINDERFREQ = 60 * 20  # Have reminders every X seconds since the last notification or since initialization.

TELEGRAM_YOURID = ""
TELEGRAM_BOTTOKEN = ""

HANDLER = None
