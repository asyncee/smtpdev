from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from mailparser import MailParser


@dataclass
class Message:
    local_message_id: str
    to: str
    subject: str
    date: dt.datetime
    html: str
    text: str
    headers: dict

    @classmethod
    def from_mailparser(cls, local_message_id: str, obj: MailParser) -> Message:
        return Message(
            local_message_id=local_message_id,
            to=cls._format_to(obj),
            subject=obj.subject,
            date=obj.date,
            html=cls._format_html(obj),
            text=cls._format_text(obj),
            headers=obj.headers,
        )

    @staticmethod
    def _format_to(obj):
        to = ", ".join([f" ".join([i for i in x if i]) for x in obj.to])
        return to or obj.headers.get("X-RcptTo", "")

    @staticmethod
    def _format_html(obj):
        return obj.text_html[0] if obj.text_html else ""

    @staticmethod
    def _format_text(obj):
        return obj.text_plain[0] if obj.text_plain else ""
