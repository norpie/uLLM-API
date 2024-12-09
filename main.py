def main():
    import cli
    args = cli.parse()
    if not args.http and not args.sockets and not args.rabbitmq:
        print(f"Please specify at least one server type to start")
        return

    import data
    data_dir = data.DataDir(args.data_dir)

    import models
    model_manager = models.ModelManager(data_dir)
    if args.http:
        import http_server
        http_server.start(args.host, args.http_port, model_manager)
    if args.sockets:
        import sockets_server
        sockets_server.start(args.host, args.sockets_port, model_manager)
    if args.rabbitmq:
        import rabbitmq
        rabbitmq.start(
            args.rabbitmq_host,
            args.rabbitmq_port,
            args.rabbitmq_vhost,
            args.rabbitmq_queue,
            args.rabbitmq_reply_queue,
            args.rabbitmq_username,
            args.rabbitmq_password,
            model_manager,
        )
    import time
    time.sleep(1)


if __name__ == "__main__":
    main()
