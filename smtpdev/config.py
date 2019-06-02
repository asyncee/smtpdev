from dataclasses import dataclass


@dataclass
class Configuration:
    smtp_host: str
    smtp_port: int
    web_host: str
    web_port: int
    develop: bool
    debug: bool
