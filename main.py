import cli
import data


def main():
    args = cli.parse()
    data_dir = data.DataDir(args.data_dir)


if __name__ == "__main__":
    main()
