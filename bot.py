import asyncio
import json
import logging
import sys
from datetime import datetime
from functools import partial

import aio_pika

import yaml
from aio_pika import Message, DeliveryMode

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')

LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

service_params = None


async def main(loop, cfg, app_name):
    connection = await aio_pika.connect_robust(
        cfg[app_name]['ampq_url'], loop=loop
    )
    # Creating channel
    channel = await connection.channel()

    # Maximum message count which will be
    # processing at the same time.
    await channel.set_qos(prefetch_count=400)

    # Declaring queue
    queue_incoming = await channel.declare_queue(
        cfg[app_name]['queue_incoming'],
        durable=True,
    )
    # arguments={
    #     'x-message-ttl': cfg[app_name]['ttl'],
    #     'x-dead-letter-exchange': cfg[app_name]['dlx_exchange'],
    #     'x-dead-letter-routing-key': cfg[app_name]['dlx_exchange_key'],
    # },

    publish_exchange = await channel.declare_exchange(
        cfg[app_name]['publish_exchange'],
        type=cfg[app_name]['publish_exchange_type'],
        durable=True,
    )

    queue_outgoing = await channel.declare_queue(
        cfg[app_name]['queue_outgoing'],
        durable=True,
    )
    # arguments={
    #     'x-message-ttl': cfg[app_name]['ttl'],
    #     'x-dead-letter-exchange': cfg[app_name]['dlx_exchange'],
    #     'x-dead-letter-routing-key': cfg[app_name]['dlx_exchange_key'],
    # },

    await queue_outgoing.bind(
        cfg[app_name]['publish_exchange'], cfg[app_name]['publish_routing_key']
    )

    await queue_incoming.consume(
        partial(
            on_message,
            cfg,
            publish_exchange,
            cfg[app_name]['publish_routing_key']
        )
    )
    return connection


async def on_message(cfg: list,
                     publish_exchange: aio_pika.exchange.Exchange, _routing_key: str,
                     message: aio_pika.IncomingMessage):
    async with message.process(ignore_processed=True):
        LOGGER.info(" [x] Received message%r" % message.body)
        # print(" [x] Received message%r" % message)
        # print("     Message body is:%r" % message.body)

        msg = json.loads(message.body)
        chat_id = "254705126329@c.us"

        LOGGER.info("---->> NEW MESSAGE")
        # LOGGER.info("Processing %s", message.body)
        try:
            d=msg

            chat_id=d['chat']['contact']['id']['_serialized']

            # DO WHATEVER YOU WANT HERE

            send_msg = {
                "message": "THIS IS A TEST MESSAGE. Waiting Implementation.\n*@Skweedudo*",
                "chat_id": chat_id,
                "type": "chat",
                "isGroup": "false" if 'g' in chat_id else 'true'
            }

            #  Sending Message Back
            _msg = Message(
                json.dumps(send_msg).encode(),
                delivery_mode=DeliveryMode.PERSISTENT
            )

            await publish_exchange.publish(_msg, routing_key=_routing_key)
            await message.ack()

        except Exception as e:
            LOGGER.exception(
                "Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {})
            )
            await message.reject(requeue=False)
        else:
            pass


def service_init(args, cfg):
    """Initialise service
    """
    if len(args) < 2:
        LOGGER.error("USAGE: python %s <app_name>" % args[0])
        exit(0)
    elif sys.argv[1] not in cfg:
        LOGGER.error('Invalid Args: App %s must be in the config file' % args[1])
        exit(0)
    else:
        LOGGER.info('%s: Started! Name: %s'
                    % (datetime.now(), args[1]))


if __name__ == "__main__":
    with open("config.yml", "r") as ymlfile:
        cnfg = yaml.load(ymlfile)

    service_init(sys.argv, cnfg)
    app_name = sys.argv[1:]

    event_loop = asyncio.get_event_loop()
    conn = event_loop.run_until_complete(main(event_loop, cnfg, app_name[0]))
    try:
        LOGGER.info('____________________________________________________________________')
        LOGGER.info('[*] Waiting for messages. Press CTRL+C to exit')
        LOGGER.info('____________________________________________________________________')
        event_loop.run_forever()
    finally:
        event_loop.run_until_complete(asyncio.sleep(0))
        conn.close()
