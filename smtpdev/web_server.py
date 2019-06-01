import asyncio
import weakref
from operator import itemgetter

import aiohttp
import aiohttp_jinja2
import bleach
import jinja2
import marshmallow as ma
from aiohttp import web
from mailparser import mailparser

from .config import Configuration
from .utils import send_test_email


class WebServer:
    def __init__(self, config: Configuration, maildir):
        self.config = config
        self.maildir = maildir
        self.app = web.Application()
        aiohttp_jinja2.setup(self.app, loader=jinja2.PackageLoader("smtpdev"))
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
        schema = UiMessageSchema()
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
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print("ws connection closed with exception %s" % ws.exception())
        finally:
            self._websockets.discard(ws)

        print("websocket connection closed")

        return ws

    def on_message(self, message):
        for ws in self._websockets:
            mail = mailparser.parse_from_string(message.as_string())
            schema = UiMessageSchema()

            asyncio.run_coroutine_threadsafe(
                ws.send_str(schema.dumps(mail)), asyncio.get_running_loop()
            )

    def send_test_email(self, request):
        send_test_email(self.config.smtp_host, self.config.smtp_port)
        return web.json_response()


class UiMessageSchema(ma.Schema):
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
