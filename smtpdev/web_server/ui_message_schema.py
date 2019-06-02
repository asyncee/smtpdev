import bleach
import marshmallow as ma
from mailparser import MailParser


class UiMessageSchema(ma.Schema):
    """Schema to serialize MailParser object."""

    to = ma.fields.String()
    subject = ma.fields.String()
    html = ma.fields.String()
    text = ma.fields.String()
    clean_text = ma.fields.String()
    date = ma.fields.DateTime()

    @ma.pre_dump
    def pre_dump(self, obj: MailParser):
        html = obj.text_html[0] if obj.text_html else ""
        text = obj.text_plain[0] if obj.text_plain else ""
        clean_text = bleach.clean(
            text=html or text,
            tags=[],
            attributes={},
            styles=[],
            protocols=[],
            strip=True,
            strip_comments=True,
        )
        return {
            "to": ", ".join([f" ".join([i for i in x if i]) for x in obj.to]),
            "subject": obj.subject,
            "html": html,
            "text": text,
            "clean_text": clean_text,
            "date": obj.date,
        }
