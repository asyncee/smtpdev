from mailbox import MaildirMessage
from typing import Collection
from typing import Type

import marshmallow as ma
from mailparser import MailParser
from mailparser import mailparser


class MailParserUtil:
    @classmethod
    def to_dict(cls, email: MailParser, schema: Type[ma.Schema]) -> dict:
        return schema().dump(email)

    @classmethod
    def to_json(cls, email: MailParser, schema: Type[ma.Schema]) -> str:
        return schema().dumps(email)

    @classmethod
    def to_dict_many(cls, emails: Collection[MailParser], schema: Type[ma.Schema]) -> dict:
        return schema(many=True).dump(emails)

    @classmethod
    def to_json_many(cls, emails: Collection[MailParser], schema: Type[ma.Schema]) -> str:
        return schema(many=True).dumps(emails)

    @classmethod
    def parse_message(cls, message: MaildirMessage) -> MailParser:
        return mailparser.parse_from_string(message.as_string())
