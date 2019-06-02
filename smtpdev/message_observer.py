import abc
import weakref
from mailbox import MaildirMessage


class MessageObserver(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def on_message(self, message: MaildirMessage):
        pass


class MessageObservable:
    def __init__(self) -> None:
        self._observers = weakref.WeakSet()

    def register(self, observer: MessageObserver):
        self._observers.add(observer)

    def notify_observers(self, message: MaildirMessage) -> None:
        for observer in self._observers:
            observer.on_message(message)
