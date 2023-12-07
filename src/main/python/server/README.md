server
======

This module provides an example architecture to show how to use the
communication and authentication plumbing provided in `gamelib` in your
project's game server implementation.

For this example, there is no game model. This example simply takes 
commands from connected clients and uses them to generate simple events
that are sent to each client in a "game" instance. 

In this example architecture `MyServer` (in the `server.py` module) is the 
central point of control. It creates and configures the listener, and it 
handles incoming connections and authentication. For each new connection,
the server finds or creates a `MyManager` object (see `manager.py`)
for the given game ID. It then hands off the connection to the manager.

A manager has an instance of `MyPublisher` (see `publisher.py`) and
a collection of controller objects -- one for each connected client. In 
the manager, a new `MyController` (see `controller.py`) is created for 
each new client connection, and the connection is added to the publisher.
After this is complete, the controller's `run` method is invoked. 

Notice that because each new client connection has its own service thread, 
the server, manager, and publisher all must account for thread safety using
locks as appropriate. In your game server, you'll also need to protect the
model from concurrent access. You could do this by introducing a lock directly
into your model, or you could "wrap" your model in another object that 
implements the same top-level interface and incorporates a lock.

The controller's `run` method simply has a loop where it waits for 
a command from the client, takes some action, and responds to the client.
Since every connected client has its own service thread, multiple clients
can be executing commands concurrently.

This example controller doesn't have a game model on which to invoke commands.
Instead, it has a simple mapping between each command and an event to be
published. Your game server's architecture will instead invoke commands
on your model. Your model will generate events which need to be delivered
by your architecture's equivalent of this example's `MyPublisher`.

Be sure to look at the `config.py` module that provides configuration
properties needed for the game server. In the other modules that use the
configuration, look for the `import` statement that imports the 
`config` module as well as references to the properties of the 
configuration such as those in `__main__.py`.
