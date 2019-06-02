from smtplib import SMTP
from typing import List

default_body = """
From: John Doe <jdoe@example.com>
To: Jane Doe <janed@example.com>
Subject: Hello!

Hi, Jane, this is me!
"""


def send_test_email(
    host: str, port: int, from_: str = "sender@example.com", to: List[str] = None, body: str = None
):
    to = to or ["recipient@example.com"]
    body = body or default_body
    client = SMTP(host, port)
    client.sendmail(from_, to, body)
