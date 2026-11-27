import json
import logging
from datetime import datetime, timezone

import aio_pika

from app.core.config import settings

logger = logging.getLogger(__name__)


async def registrar_evento(
    acao: str,
    entidade: str,
    entidade_id: str,
    usuario_id: str,
    detalhes: dict | None = None,
) -> None:
    evento = {
        "acao": acao,
        "entidade": entidade,
        "entidade_id": entidade_id,
        "usuario_id": usuario_id,
        "detalhes": detalhes or {},
        "ocorrido_em": datetime.now(timezone.utc).isoformat(),
    }
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("audit.logs", durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(evento, ensure_ascii=False).encode("utf-8"),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type="application/json",
                ),
                routing_key=queue.name,
            )
    except Exception:
        logger.exception("Não foi possível publicar evento de auditoria.")
