import marshmallow as ma


class MessageSchema(ma.Schema):
    local_message_id = ma.fields.String()
    to = ma.fields.String()
    subject = ma.fields.String()
    date = ma.fields.DateTime()


class FullMessageSchema(MessageSchema):
    html = ma.fields.String()
    text = ma.fields.String()
    headers = ma.fields.Dict()
