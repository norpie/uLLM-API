import argparse


def parse():
    parser = argparse.ArgumentParser(
        description="uLLM-API: A simple HTTP API for running LLM's."
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="The host to run the server on. (0.0.0.0 for all interfaces)",
    )
    parser.add_argument(
        "--http",
        type=bool,
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Whether to run the http server.",
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=8080,
        help="The port to run the http server on.",
    )
    parser.add_argument(
        "--sockets",
        type=bool,
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Whether to run the websocket server.",
    )
    parser.add_argument(
        "--sockets-port",
        type=str,
        default=8081,
        help="The port to run the websocket server on.",
    )
    parser.add_argument(
        "--rabbitmq",
        type=bool,
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Whether to run the rabbitmq server.",
    )
    parser.add_argument(
        "--rabbitmq-host",
        type=str,
        default="localhost",
        help="The host to run the rabbitmq server on.",
    )
    parser.add_argument(
        "--rabbitmq-port",
        type=int,
        default=5672,
        help="The port to run the rabbitmq server on.",
    )
    parser.add_argument(
        "--rabbitmq-vhost",
        type=str,
        default="/",
        help="The vhost to use for rabbitmq.",
    )
    parser.add_argument(
        "--rabbitmq-queue",
        type=str,
        default="ullm",
        help="The queue to listen on for rabbitmq.",
    )
    parser.add_argument(
        "--rabbitmq-reply-queue",
        type=str,
        default="ullm.reply",
        help="The queue ullm publishes responses to.",
    )
    parser.add_argument(
        "--rabbitmq-username",
        type=str,
        default="guest",
        help="The username for rabbitmq.",
    )
    parser.add_argument(
        "--rabbitmq-password",
        type=str,
        default="guest",
        help="The password for rabbitmq.",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="$XDG_DATA_HOME/ullm-api",
        help="The directory to store the data and models in.",
    )
    return parser.parse_args()
