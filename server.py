import asyncio
import os
from dataclasses import dataclass
from mailbox import Maildir
from operator import itemgetter
from tempfile import TemporaryDirectory

import aiohttp
import aiohttp_jinja2
import bleach
import jinja2
import marshmallow as ma
from aiohttp import web
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Mailbox
from mailparser import mailparser


@dataclass
class Configuration:
    smtp_host: str
    smtp_port: int
    web_host: str
    web_port: int


class MessageSchema(ma.Schema):
    to = ma.fields.String()
    subject = ma.fields.String()
    html = ma.fields.String()
    text = ma.fields.String()
    clean_text = ma.fields.String()
    date = ma.fields.DateTime()

    @ma.pre_dump
    def pre_dump(self, obj):
        html = obj.text_html[0]
        text = obj.text_plain[0]
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


class WebServer:
    def __init__(self, config: Configuration, maildir):
        self.config = config
        self.maildir = maildir
        self.app = web.Application()
        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader("templates"))
        routes = [
            web.get("/", self.view_index),
            web.get("/messages", self.view_messages_json),
            web.get("/ws", self.websocket_handler),
        ]
        self.app.add_routes(routes)

    def start(self):
        # fixme: use loop
        web.run_app(self.app, host=self.config.web_host, port=self.config.web_port)

    def _get_messages(self):
        messages = sorted(self.maildir, key=itemgetter("message-id"))

        items = []
        for message in messages:
            mail = mailparser.parse_from_string(message.as_string())
            items.append(mail)

        return items

    def _get_messages_json(self):
        messages = self._get_messages()
        response = []
        schema = MessageSchema()
        for message in messages:
            response.append(schema.dump(message))
        return response

    async def view_messages_json(self, request):
        return web.json_response(self._get_messages_json())

    @aiohttp_jinja2.template("index.html")
    async def view_index(self, request):
        messages = self._get_messages_json()
        return {
            "smtp_host": self.config.smtp_host,
            "smtp_port": self.config.smtp_port,
            "messages": messages,
        }

    async def websocket_handler(self, request):

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == "close":
                    await ws.close()
                else:
                    await ws.send_str(msg.data + "/answer")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print("ws connection closed with exception %s" % ws.exception())

        print("websocket connection closed")

        return ws


if __name__ == "__main__":
    with TemporaryDirectory() as dir:
        config = Configuration(
            smtp_host="localhost", smtp_port=2500, web_host="localhost", web_port=8080
        )

        dir = "/tmp/dir"
        print(dir)

        loop = asyncio.new_event_loop()

        class MailboxHandler(Mailbox):
            def handle_message(self, message):
                super().handle_message(message)
                # TODO: notify observer of new message
                #   and subscribe in websocket

        maildir_path = os.path.join(dir, "maildir")
        maildir = Maildir(maildir_path)
        mailbox = MailboxHandler(maildir_path)

        controller = Controller(
            mailbox, loop=loop, hostname=config.smtp_host, port=config.smtp_port
        )
        controller.start()

        web_server = WebServer(config, maildir)
        web_server.start()

        controller.stop()
