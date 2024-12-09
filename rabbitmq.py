import asyncio
import pika
import json
import functools

from models import ModelManager
from request import IResponder, Request, Response


def start(
    host: str,
    port: int,
    vhost: str,
    queue: str,
    reply_queue: str,
    username: str,
    password: str,
    model_manager: ModelManager,
):
    import threading

    thread = threading.Thread(
        target=run,
        args=(host, port, vhost, queue, reply_queue, username, password, model_manager),
    )
    thread.start()


def run(
    host: str,
    port: int,
    vhost: str,
    queue: str,
    reply_queue: str,
    username: str,
    password: str,
    model_manager: ModelManager,
):
    print(
        f"Starting rabbitmq connection on `amqp://{host}:{port}{vhost}` with queue `{queue}` and reply queue `{reply_queue}`"
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host, port, vhost, pika.PlainCredentials(username, password)
        )
    )
    callback_datad = functools.partial(
        callback, model_manager=model_manager, reply_queue=reply_queue
    )

    sub = connection.channel()
    sub.queue_declare(queue=queue)
    sub.queue_declare(queue=reply_queue)
    sub.basic_consume(queue, on_message_callback=callback_datad)

    try:
        print("Starting consuming")
        sub.start_consuming()
        print("Consuming started")
    except KeyboardInterrupt:
        print("Stopping consuming")
        sub.stop_consuming()
        print("Consuming stopped")
    connection.close()
    print("Connection closed")


class RabbitMQResponder(IResponder):
    def __init__(self, channel, reply_queue):
        self.channel = channel
        self.reply_queue = reply_queue

    async def raw_response(self, response):
        self.channel.basic_publish(
            exchange="", routing_key=self.reply_queue, body=response.toJSON()
        )

    async def response(self, response):
        await self.raw_response(response)

    async def intermediate_response(self, response):
        await self.raw_response(response)


def sync(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))

    return wrapper


@sync
async def callback(channel, method, properties, body, model_manager, reply_queue):
    print("Received message")
    responder = RabbitMQResponder(channel, reply_queue)
    try:
        print(f"Handling request: {str(body)}")
        request = Request.from_json(body)
        print(f"Request: {request}")
        await request.handle(model_manager, responder)
        print("Request handled")
    except Exception as e:
        print(f"Error handling request: {str(e)}")
        await Response.new_no_id_error(str(e)).send(responder)
    channel.basic_ack(delivery_tag=method.delivery_tag)
