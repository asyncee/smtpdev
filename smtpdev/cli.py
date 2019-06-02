import logging
import pathlib
from contextlib import nullcontext
from mailbox import Maildir
from tempfile import TemporaryDirectory

import click
from aiosmtpd.controller import Controller

from .config import Configuration
from .handlers import MailboxHandler
from .web_server import WebServer

logger = logging.getLogger(__name__)


@click.command()
@click.option("--smtp-host", default="localhost")
@click.option("--smtp-port", default=2500)
@click.option("--web-host", default="localhost")
@click.option("--web-port", default=8080)
@click.option("--develop", default=False, is_flag=True)
@click.option("--debug", default=False, is_flag=True)
@click.option("--maildir", default=None)
def main(smtp_host, smtp_port, web_host, web_port, develop, debug, maildir):
    logging.basicConfig(level=logging.DEBUG)

    logger.info("SMTP server is running on %s:%s", smtp_host, smtp_port)
    logger.info("Web server is running on %s:%s", web_host, web_port)

    if develop:
        logger.info("Running in developer mode")
        debug = True

    dir_context = TemporaryDirectory() if maildir is None else nullcontext(maildir)

    with dir_context as maildir_path:
        logger.info("Mail directory: %s", maildir_path)

        config = Configuration(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            web_host=web_host,
            web_port=web_port,
            develop=develop,
            debug=debug,
        )

        pathlib.Path(maildir_path).mkdir(parents=True, exist_ok=True)
        maildir = Maildir(maildir_path)
        mailbox = MailboxHandler(maildir_path)

        controller = Controller(mailbox, hostname=config.smtp_host, port=config.smtp_port)
        web_server = WebServer(config, maildir)
        mailbox.register_message_observer(web_server)

        controller.start()
        web_server.start()
        controller.stop()
