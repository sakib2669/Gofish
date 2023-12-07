import argparse
import logging

import api.config as config

from .app import app


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--debug", action="store_true", help="enable debug logging")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s %(threadName)s %(message)s")

    app.run(host=config.LOCAL_IP, port=int(config.API_PORT), debug=args.debug)
