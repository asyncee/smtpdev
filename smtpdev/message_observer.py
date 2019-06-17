import abc
import weakref
from mailbox import MaildirMessage
from typing import MutableSet


class MessageObserver(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def on_message(self, local_message_id: str, message: MaildirMessage):
        pass


class MessageObservable:
    def __init__(self) -> None:
        self._observers: MutableSet[MessageObserver] = weakref.WeakSet()

    def register(self, observer: MessageObserver):
        self._observers.add(observer)

    def notify_observers(self, local_message_id: str, message: MaildirMessage) -> None:
        for observer in self._observers:
            observer.on_message(local_message_id, message)
