from mailbox import MaildirMessage

from mailparser import MailParser
from mailparser import mailparser

from .ui_message_schema import UiMessageSchema


class MailParserUtil:
    schema = UiMessageSchema()

    @classmethod
    def to_dict(cls, email: MailParser) -> dict:
        return cls.schema.dump(email)

    @classmethod
    def to_json(cls, email: MailParser) -> str:
        return cls.schema.dumps(email)

    @classmethod
    def parse_message(cls, message: MaildirMessage) -> MailParser:
        return mailparser.parse_from_string(message.as_string())
