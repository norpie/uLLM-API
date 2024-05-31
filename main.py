import cli
import data
import models
import web


def main():
    args = cli.parse()
    data_dir = data.DataDir(args.data_dir)
    model_manager = models.ModelManager(data_dir)
    web.run(args.host, args.port, model_manager)


if __name__ == "__main__":
    main()
