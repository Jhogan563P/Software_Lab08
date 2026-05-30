from dataclasses import dataclass
import os


@dataclass(frozen=True)
class RabbitSettings:
    host: str = os.getenv("RABBIT_HOST", "localhost")
    port: int = int(os.getenv("RABBIT_PORT", 5672))
    username: str = os.getenv("RABBIT_USER", "guest")
    password: str = os.getenv("RABBIT_PASS", "guest")
    vhost: str = os.getenv("RABBIT_VHOST", "/")


@dataclass(frozen=True)
class AppSettings:
    rabbit: RabbitSettings = RabbitSettings()
