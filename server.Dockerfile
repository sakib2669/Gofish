# This Dockerfile provides an example that you can reuse in your project
# It copies the game server source from the `server` module, and the
# public key generated during the setup (see the top level README for details),
# placing these artifacts into the container's /app directory. It installs the
# dependencies for the game server, and configures the container to run the
# server module by default.

FROM python:3.11-slim
WORKDIR /app
#COPY src/main/python/model/ /app/model/
COPY src/main/python/server/ /app/server/
COPY public_key.pem /app/
RUN python3 -m pip install vtece4564-gamelib
CMD ["/usr/local/bin/python3", "-m", "server"]

# Docker experts will want to optimize the order of the directives in
# this file. Ideally, the RUN directive that installs the dependencies
# should be placed before the COPY directives that install the program
# code. This would make better use of the image cache. However, changing
# the order means that you'll need to pin the version for vtece4564-gamelib
# and you'll need to update the version as needed. In the current ordering
# of the directives, the latest version of the game library will be installed
# each time the image is built.
