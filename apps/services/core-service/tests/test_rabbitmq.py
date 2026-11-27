
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.rabbitmq import publish_event


@pytest.mark.anyio
async def test_publicar_evento():
    connection = MagicMock()
    connection.__aenter__ = AsyncMock(return_value=connection)
    connection.__aexit__ = AsyncMock(return_value=None)

    channel = MagicMock()
    channel.default_exchange.publish = AsyncMock()

    connection.channel = AsyncMock(return_value=channel)

    queue = MagicMock()
    queue.name = "fila_teste"
    channel.declare_queue = AsyncMock(return_value=queue)

    event_data = {
        "hotel_id": "123",
        "nome": "Hotel Teste",
    }

    with patch(
        "app.core.rabbitmq.aio_pika.connect_robust",
        new_callable=AsyncMock,
    ) as connect_mock:
        connect_mock.return_value = connection
         
        with patch(
            "app.core.rabbitmq.aio_pika.Message",
            side_effect=lambda **kwargs: kwargs,
        ) as message_mock:

            await publish_event("fila_teste", event_data)

    connect_mock.assert_awaited_once()
    connection.channel.assert_awaited_once_with()

    channel.declare_queue.assert_awaited_once_with(
        "fila_teste",
        durable=True,
    )

    message_mock.assert_called_once()
    mensagem = message_mock.call_args.kwargs

    assert mensagem["body"] == (
        b'{"hotel_id": "123", "nome": "Hotel Teste"}'
    )

    channel.default_exchange.publish.assert_awaited_once_with(
        mensagem,
        routing_key="fila_teste",
    )
