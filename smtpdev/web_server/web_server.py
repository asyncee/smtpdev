import asyncio
import inspect
import logging
import weakref
from mailbox import Maildir
from mailbox import MaildirMessage
from pathlib import Path
from typing import MutableSet

import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web
from mailparser import MailParser

import smtpdev
from . import schemas
from .mailparser_util import MailParserUtil
from ..config import Configuration
from ..message_observer import MessageObserver


class WebServer(MessageObserver):
    def __init__(self, config: Configuration, maildir: Maildir):
        self._config = config
        self._maildir = maildir
        self._websockets: MutableSet[web.WebSocketResponse] = weakref.WeakSet()
        self._app = self._configure_webapp()
        self._logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        web.run_app(self._app, host=self._config.web_host, port=self._config.web_port)

    @aiohttp_jinja2.template("index.html")
    async def page_index(self, request):
        return {
            "smtp_host": self._config.smtp_host,
            "smtp_port": self._config.smtp_port,
            "develop": self._config.develop,
            "messages": MailParserUtil.to_json_many(self._get_messages(), schemas.MessageSchema),
        }

    async def message_details(self, request):
        message_id = request.query.get("message-id")
        message = self._get_message(message_id)
        if not message:
            return web.json_response(
                {"status": "error", "message": "message not found"}, status=404
            )
        return web.json_response(MailParserUtil.to_dict(message, schemas.FullMessageSchema))

    async def list_all_messages(self, request):
        messages = self._get_messages()
        return web.json_response(MailParserUtil.to_dict_many(messages, schemas.MessageSchema))

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

    def on_message(self, message: MaildirMessage):
        for ws in self._websockets:
            mail = self._parse_message(message)
            coro = ws.send_str(MailParserUtil.to_json(mail, schemas.MessageSchema))
            asyncio.run_coroutine_threadsafe(coro, asyncio.get_running_loop())

    def _configure_webapp(self):
        static_path = Path(inspect.getfile(smtpdev)).parent / "static"

        app = web.Application()
        aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader("smtpdev"))
        routes = [
            web.get("/", self.page_index),
            web.get("/message", self.message_details),
            web.get("/messages", self.list_all_messages),
            web.get("/ws", self.websocket_handler),
            web.static("/static", static_path),
        ]
        app.add_routes(routes)
        return app

    def _get_messages(self):
        items = []
        for message_id, message in self._maildir.items():
            items.append(self._parse_message(message))

        return items

    def _get_message(self, message_id: str):
        return self._parse_message(self._maildir.get(message_id))

    def _parse_message(self, message: MaildirMessage) -> MailParser:
        return MailParserUtil.parse_message(message)
