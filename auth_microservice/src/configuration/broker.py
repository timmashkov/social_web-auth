import json
from dataclasses import asdict

from typing import Any
from uuid import uuid4

import aio_pika
from aio_pika.message import Message
from sqlalchemy.orm import DeclarativeMeta

from configuration.core.config import base_config


class BaseMQ:
    """Базовый класс для брокера, принимает ЮРЛ, содержит статики для энкода/декода"""

    def __init__(self, mq_url: str) -> None:
        self.mq_url = mq_url
        self.connection = None
        self.channel = None

    @staticmethod
    def serialize_data(data: Any) -> bytes:
        def custom_serializer(obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                return asdict(obj)

        return json.dumps(data, default=custom_serializer).encode()

    @staticmethod
    def deserialize_data(data: bytes) -> Any:
        return json.loads(data)


class MessageQueue(BaseMQ):
    """Класс брокера, имплементирует коннкект и ченл, посылает мессагу и слушает очередь"""

    async def mq_connect(self):
        self.connection = await aio_pika.connect_robust(self.mq_url)
        self.channel = await self.connection.channel()
        print("RabbitMQ connection is now available")

    async def mq_close_conn(self):
        await self.connection.close()

    async def send_message(self, queue_name: str, data: Any):
        message = Message(
            body=self.serialize_data(data=data),
            content_type="application/social_web",
            correlation_id=str(uuid4()),
        )
        await self.channel.default_exchange.publish(message, queue_name)

    async def listen_queue(self, func, queue_name: str, auto_delete: bool = False):
        queue = await self.channel.declare_queue(
            queue_name, auto_delete=auto_delete, durable=True
        )
        async with queue.iterator() as que_iter:
            async for message in que_iter:
                await func(message)


mq = MessageQueue(base_config.RMQ_URL)
