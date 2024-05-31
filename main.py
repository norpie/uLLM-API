import cli
import data
import web


def main():
    args = cli.parse()
    data_dir = data.DataDir(args.data_dir)
    web.run(args.host, args.port, data_dir)


if __name__ == "__main__":
    main()
