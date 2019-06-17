from mailbox import MaildirMessage
from typing import Collection
from typing import Type

import marshmallow as ma
from mailparser import mailparser

from .message import Message


class MessageUtil:
    @classmethod
    def to_dict(cls, message: Message, schema: Type[ma.Schema]) -> dict:
        return schema().dump(message)

    @classmethod
    def to_json(cls, message: Message, schema: Type[ma.Schema]) -> str:
        return schema().dumps(message)

    @classmethod
    def to_dict_many(cls, emails: Collection[Message], schema: Type[ma.Schema]) -> dict:
        return schema(many=True).dump(emails)

    @classmethod
    def to_json_many(cls, emails: Collection[Message], schema: Type[ma.Schema]) -> str:
        return schema(many=True).dumps(emails)

    @classmethod
    def parse_message(cls, local_message_id: str, message: MaildirMessage) -> Message:
        obj = mailparser.parse_from_string(message.as_string())
        return Message.from_mailparser(local_message_id=local_message_id, obj=obj)
