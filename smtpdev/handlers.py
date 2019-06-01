import datetime as dt
from email.utils import format_datetime

from aiosmtpd.handlers import Mailbox


class MailboxHandler(Mailbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observers = set()

    def handle_message(self, message):
        if message["Date"] is None:
            message["Date"] = format_datetime(dt.datetime.now())
        super().handle_message(message)
        self.notify_observers(message)

    def register(self, observer):
        self.observers.add(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.on_message(message)
