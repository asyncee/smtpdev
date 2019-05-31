from smtplib import SMTP


def send_smtp(host, port):
    client = SMTP(host, port)
    client.sendmail(
        "aperson@example.com",
        ["bperson@example.com"],
        """\
    From: Anne Person <anne@example.com>
    To: Bart Person <bart@example.com>
    Subject: A test
    Message-ID: <ant>

    Hi Bart, this is Anne.
    """,
    )


# Date: 2 Nov 81 22:33:44
