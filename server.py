import asyncio
import datetime as dt
import os
import weakref
from dataclasses import dataclass
from email.utils import format_datetime
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

from send import send_smtp


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


class WSMessage(ma.Schema):
    type = ma.fields.String()
    data = ma.fields.Nested(MessageSchema())


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
            web.get("/send-test-email", self.send_test_email),
        ]
        self.app.add_routes(routes)
        self._websockets = weakref.WeakSet()

    def start(self):
        # fixme: use loop
        web.run_app(self.app, host=self.config.web_host, port=self.config.web_port)

    def _get_messages(self):
        messages = sorted(self.maildir, key=itemgetter("date"), reverse=True)

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

        self._websockets.add(ws)
        print("added websocket")

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == "close":
                        await ws.close()
                    else:
                        await ws.send_str(msg.data + "/answer")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print("ws connection closed with exception %s" % ws.exception())
        finally:
            self._websockets.discard(ws)

        print("websocket connection closed")

        return ws

    def on_message(self, message):
        for ws in self._websockets:
            mail = mailparser.parse_from_string(message.as_string())
            schema = WSMessage()
            msg = {"type": "message", "data": mail}

            asyncio.run_coroutine_threadsafe(
                ws.send_str(schema.dumps(msg)), asyncio.get_running_loop()
            )

    def send_test_email(self, request):
        send_smtp(self.config.smtp_host, self.config.smtp_port)
        return web.json_response()


if __name__ == "__main__":
    with TemporaryDirectory() as dir:
        config = Configuration(
            smtp_host="localhost", smtp_port=2500, web_host="localhost", web_port=8080
        )

        dir = "/tmp/dir"
        print(dir)

        loop = asyncio.new_event_loop()

        class MailboxHandler(Mailbox):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.observers = set()

            def handle_message(self, message):
                if message["Date"] is None:
                    message["Date"] = format_datetime(dt.datetime.now())
                super().handle_message(message)
                self.notify_observers(message)

            def register(self, observer):
                self.observers.add(observer)

            def notify_observers(self, message):
                for observer in self.observers:
                    observer.on_message(message)

        maildir_path = os.path.join(dir, "maildir")
        maildir = Maildir(maildir_path)
        mailbox = MailboxHandler(maildir_path)

        controller = Controller(
            mailbox, loop=loop, hostname=config.smtp_host, port=config.smtp_port
        )

        web_server = WebServer(config, maildir)
        mailbox.register(web_server)

        controller.start()
        web_server.start()
        controller.stop()
