import datetime as dt
from email.utils import format_datetime

from aiosmtpd.handlers import Mailbox

from smtpdev.message_observer import MessageObserver
from .message_observer import MessageObservable


class MailboxHandler(Mailbox):
    def __init__(self, mail_dir: str, message_class=None):
        super().__init__(mail_dir, message_class)
        self._observable = MessageObservable()

    def register_message_observer(self, observer: MessageObserver):
        self._observable.register(observer)

    def handle_message(self, message):
        if message["Date"] is None:
            message["Date"] = format_datetime(dt.datetime.now())
        super().handle_message(message)
        self._observable.notify_observers(message)
