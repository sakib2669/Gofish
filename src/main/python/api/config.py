import os

# Instead of simply defining constants for various configuration parameters in
# the modules that need them, we instead define all the configurable
# properties in this module. This not only defines all the configuration in one
# place, but also allows us to override any of this configuration using
# environment variables whose names match the property name.
#
# We provide a default value for each configuration property that allows you to
# run the game server locally (e.g. from a shell in a terminal) without needing to
# specify any configuration properties. Notice that because environment variable
# values are always strings, we specify all the defaults as strings as well.
# For properties such as port numbers, you'll need to convert the string to the
# appropriate type before using it. See `__main__.py` for an example.
#
# When running the API from Docker Compose, we'll override several of these
# properties.

LOCAL_IP = os.environ.get("LOCAL_IP", "127.0.0.1")
API_PORT = os.environ.get("API_PORT", "10021")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017/game-db")

TOKEN_ISSUER_URI = os.environ.get("TOKEN_ISSUER_URI", "urn:ece4564:token-issuer")
PRIVATE_KEY_FILE = os.environ.get("PRIVATE_KEY_FILE", "private_key.pem")
PRIVATE_KEY_PASSPHRASE = os.environ.get("PRIVATE_KEY_PASSPHRASE", "secret")

GAME_SERVER_HOST = os.environ.get("GAME_SERVER_HOST", "localhost")
GAME_SERVER_WS_SCHEME = os.environ.get("GAME_SERVER_WS_SCHEME", "ws")
GAME_SERVER_WS_PORT = os.environ.get("GAME_SERVER_WS_PORT", "10020")
