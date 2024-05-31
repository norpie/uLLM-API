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
        "--port",
        type=int,
        default=8080,
        help="The port to run the server on.",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="$XDG_DATA_HOME/ullm-api",
        help="The directory to store the data and models in.",
    )
    return parser.parse_args()
