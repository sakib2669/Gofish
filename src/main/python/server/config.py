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
# When running the game server from Docker Compose, we'll override several of these
# properties.


LOCAL_IP = os.environ.get("LOCAL_IP", "127.0.0.1")
WS_LISTENER_PORT = os.environ.get("WS_LISTENER_PORT", "10020")

ENABLE_AUTH = os.environ.get("ENABLE_AUTH")
TOKEN_ISSUER_URI = os.environ.get("TOKEN_ISSUER_URI", "urn:ece4564:token-issuer")
PUBLIC_KEY_FILE = os.environ.get("PUBLIC_KEY_FILE", "public_key.pem")
