import cli
import data
from engines.engine import EngineType
import models
import time
import http_server
import sockets_server


def main():
    args = cli.parse()
    if not args.http and not args.sockets:
        print(f"Please specify at least one server type to start")
        return
    data_dir = data.DataDir(args.data_dir)
    model_manager = models.ModelManager(data_dir)
    if args.http:
        http_server.start(args.host, args.http_port, model_manager)
    if args.sockets:
        sockets_server.start(args.host, args.sockets_port, model_manager)
    time.sleep(1)


if __name__ == "__main__":
    main()
