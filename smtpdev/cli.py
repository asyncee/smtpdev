import asyncio
import os
from mailbox import Maildir
from tempfile import TemporaryDirectory

import click
from aiosmtpd.controller import Controller

from .config import Configuration
from .handlers import MailboxHandler
from .web_server import WebServer


@click.command()
@click.option("--smtp-host", default="localhost")
@click.option("--smtp-port", default=2500)
@click.option("--web-host", default="localhost")
@click.option("--web-port", default=8080)
def main(smtp_host, smtp_port, web_host, web_port):
    with TemporaryDirectory() as tempdir:
        config = Configuration(
            smtp_host=smtp_host, smtp_port=smtp_port, web_host=web_host, web_port=web_port
        )

        loop = asyncio.new_event_loop()

        maildir_path = os.path.join(tempdir, "maildir")
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
