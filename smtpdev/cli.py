import logging
import pathlib
from contextlib import nullcontext
from mailbox import Maildir
from tempfile import TemporaryDirectory

import click
from aiosmtpd.controller import Controller

from .config import Configuration
from .smtp_handlers import MailboxHandler
from .web_server import WebServer

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--smtp-host",
    envvar="SMTPDEV_SMTP_HOST",
    default="localhost",
    help="Smtp server host (default localhost).",
)
@click.option(
    "--smtp-port", envvar="SMTPDEV_SMTP_PORT", default=2500, help="Smtp server port (default 2500)."
)
@click.option(
    "--web-host",
    envvar="SMTPDEV_WEB_HOST",
    default="localhost",
    help="Web server host (default localhost).",
)
@click.option(
    "--web-port", envvar="SMTPDEV_WEB_PORT", default=8080, help="Web server port (default 8080)."
)
@click.option(
    "--develop",
    envvar="SMTPDEV_DEVELOP",
    default=False,
    is_flag=True,
    help="Run in developer mode.",
)
@click.option(
    "--debug",
    envvar="SMTPDEV_DEBUG",
    default=False,
    is_flag=True,
    help="Whether to use debug loglevel.",
)
@click.option(
    "--maildir",
    envvar="SMTPDEV_MAILDIR",
    default=None,
    help="Full path to emails directory, temporary directory if not set.",
)
def main(smtp_host, smtp_port, web_host, web_port, develop, debug, maildir):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger.info("SMTP server is running on %s:%s", smtp_host, smtp_port)
    logger.info("Web server is running on %s:%s", web_host, web_port)

    if develop:
        logger.info("Running in developer mode")

    dir_context = TemporaryDirectory if maildir is None else lambda: nullcontext(maildir)

    with dir_context() as maildir_path:
        maildir_path = pathlib.Path(maildir_path)
        maildir_path.mkdir(parents=True, exist_ok=True)

        logger.info("Mail directory: %s", maildir_path)

        config = Configuration(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            web_host=web_host,
            web_port=web_port,
            develop=develop,
            debug=debug,
        )

        maildir = Maildir(maildir_path / "maildir")
        mailbox = MailboxHandler(maildir_path / "maildir")

        controller = Controller(mailbox, hostname=config.smtp_host, port=config.smtp_port)
        web_server = WebServer(config, maildir)
        mailbox.register_message_observer(web_server)

        controller.start()
        web_server.start()
        controller.stop()
