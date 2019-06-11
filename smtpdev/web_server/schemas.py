import marshmallow as ma


class MessageSchema(ma.Schema):
    message_id = ma.fields.String()
    to = ma.fields.Method("format_to")
    subject = ma.fields.String()
    date = ma.fields.DateTime()

    def format_to(self, obj):
        return ", ".join([f" ".join([i for i in x if i]) for x in obj.to])


class FullMessageSchema(MessageSchema):
    html = ma.fields.Method("format_html")
    text = ma.fields.Method("format_text")
    headers = ma.fields.Dict()

    def format_html(self, obj):
        return obj.text_html[0] if obj.text_html else ""

    def format_text(self, obj):
        return obj.text_plain[0] if obj.text_plain else ""
