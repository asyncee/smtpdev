import asyncio
import logging
import weakref
from mailbox import Maildir
from mailbox import MaildirMessage
from operator import itemgetter
from typing import Dict
from typing import List
from typing import Union

import aiohttp
import aiohttp_jinja2
import bleach
import jinja2
import marshmallow as ma
from aiohttp import web
from mailparser import MailParser
from mailparser import mailparser

from .config import Configuration
from .message_observer import MessageObserver
from .utils import send_test_email


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


def serialize_email(email: MailParser, as_json=False) -> Union[Dict, str]:
    schema = UiMessageSchema()
    dump_method = schema.dumps if as_json else schema.dump
    return dump_method(email)


def parse_message(message: MaildirMessage) -> MailParser:
    return mailparser.parse_from_string(message.as_string())


class WebServer(MessageObserver):
    def __init__(self, config: Configuration, maildir: Maildir):
        self._config = config
        self._maildir = maildir
        self._websockets = weakref.WeakSet()
        self._app = self._configure_webapp()
        self._logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        web.run_app(self._app, host=self._config.web_host, port=self._config.web_port)

    async def view_messages_json(self, request):
        return web.json_response(self._get_messages_json())

    @aiohttp_jinja2.template("index.html")
    async def view_index(self, request):
        messages = self._get_messages_json()
        return {
            "smtp_host": self._config.smtp_host,
            "smtp_port": self._config.smtp_port,
            "messages": messages,
            "develop": self._config.develop,
        }

    async def websocket_handler(self, request):

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self._websockets.add(ws)
        self._logger.debug("New websocket connection established")

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.ERROR:
                    self._logger.debug(
                        "Websocket connection closed with exception %s", ws.exception()
                    )
        finally:
            self._websockets.discard(ws)

        self._logger.debug("Websocket connection closed")

        return ws

    async def send_test_email(self, request):
        send_test_email(self._config.smtp_host, self._config.smtp_port)
        return web.Response()

    def on_message(self, message: MaildirMessage):
        for ws in self._websockets:
            mail = parse_message(message)

            asyncio.run_coroutine_threadsafe(
                ws.send_str(serialize_email(mail, as_json=True)), asyncio.get_running_loop()
            )

    def _configure_webapp(self):
        app = web.Application()
        aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader("smtpdev"))
        routes = [
            web.get("/", self.view_index),
            web.get("/messages", self.view_messages_json),
            web.get("/ws", self.websocket_handler),
            web.get("/send-test-email", self.send_test_email),
        ]
        app.add_routes(routes)
        return app

    def _get_messages(self):
        messages: List[MaildirMessage] = sorted(self._maildir, key=itemgetter("date"), reverse=True)

        items = []
        for message in messages:
            items.append(parse_message(message))

        return items

    def _get_messages_json(self):
        messages = self._get_messages()
        response = []
        for message in messages:
            response.append(serialize_email(message))
        return response
