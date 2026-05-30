from fastapi import HTTPException

from app.shared.config.settings import AppSettings
from app.shared.messaging.rabbitmq import RabbitConnectionFactory


def rabbit_healthcheck(settings: AppSettings | None = None) -> dict:
    factory = RabbitConnectionFactory(settings or AppSettings())
    connection = None
    try:
        connection = factory.create_connection()
        return {"status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    finally:
        if connection and connection.is_open:
            connection.close()
