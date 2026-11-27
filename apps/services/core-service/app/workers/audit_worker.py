import asyncio
import json
from datetime import datetime, timezone

import aio_pika
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
audit_collection = mongo_client[settings.MONGODB_DB]["logs_auditoria"]


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process(requeue=True):
        data = json.loads(message.body.decode("utf-8"))
        log_document = {
            **data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await audit_collection.insert_one(log_document)
        print("[Worker] Log registrado com sucesso no MongoDB!")


async def main():
    print("[Worker] Conectando ao RabbitMQ.")
    await mongo_client.admin.command("ping")
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue("audit.logs", durable=True)
        print("[Worker] Aguardando mensagens na fila 'audit.logs'...")
        await queue.consume(process_message)
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Worker] Parado pelo usuário.")
    finally:
        mongo_client.close()
