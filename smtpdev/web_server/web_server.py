import asyncio
import inspect
import logging
import weakref
from mailbox import Maildir
from mailbox import MaildirMessage
from operator import itemgetter
from pathlib import Path
from typing import List
from typing import MutableSet

import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

import smtpdev
from .mailparser_util import MailParserUtil
from ..config import Configuration
from ..message_observer import MessageObserver
from ..utils.smtp import send_test_email


class WebServer(MessageObserver):
    def __init__(self, config: Configuration, maildir: Maildir):
        self._config = config
        self._maildir = maildir
        self._websockets: MutableSet[web.WebSocketResponse] = weakref.WeakSet()
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
            mail = MailParserUtil.parse_message(message)
            coro = ws.send_str(MailParserUtil.to_json(mail))
            asyncio.run_coroutine_threadsafe(coro, asyncio.get_running_loop())

    def _configure_webapp(self):

        static_path = Path(inspect.getfile(smtpdev)).parent / "static"

        app = web.Application()
        aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader("smtpdev"))
        routes = [
            web.get("/", self.view_index),
            web.get("/messages", self.view_messages_json),
            web.get("/ws", self.websocket_handler),
            web.get("/send-test-email", self.send_test_email),
            web.static("/static", static_path),
        ]
        app.add_routes(routes)
        return app

    def _get_messages(self):
        messages: List[MaildirMessage] = sorted(self._maildir, key=itemgetter("date"), reverse=True)

        items = []
        for message in messages:
            items.append(MailParserUtil.parse_message(message))

        return items

    def _get_messages_json(self):
        messages = self._get_messages()
        response = []
        for message in messages:
            response.append(MailParserUtil.to_dict(message))
        return response
