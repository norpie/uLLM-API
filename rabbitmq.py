import pika
import json
import functools

from models import ModelManager


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
        sub.start_consuming()
    except KeyboardInterrupt:
        sub.stop_consuming()


def callback(channel, method, properties, body, model_manager, reply_queue):
    try:
        dict = json.loads(body)
        body = json.dumps(model_manager.model_status())
    except json.JSONDecodeError as e:
        body = json.dumps({"error": "Invalid message"})
    except Exception as e:
        body = json.dumps({"error": "Internal error"})
    channel.basic_publish(exchange="", routing_key=reply_queue, body=body)
    channel.basic_ack(delivery_tag=method.delivery_tag)
