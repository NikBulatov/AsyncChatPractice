Server module
================================================

Messenger server module. Processes dictionaries - messages, stores public keys of clients.

Usage

The module supports command line arguments:

1. -p - Port on which connections are accepted
2. -a - Address from which connections are accepted.
3. --no_gui Run only basic functions, without a graphical shell.

* Only 1 command is supported in this mode: exit - shutdown.

Examples of using:

``python server.py -p 8080``

*Run server on port 8080*

``python server.py -a localhost``

*Starting a server that only accepts connections from localhost*

``python server.py --no-gui``

*Launch without GUI*

server.py
~~~~~~~~~

A executable module that contains a command line argument parser and application initialization functionality.

server.**arg_parser**()
    Command line argument parser, returns a tuple of 4 elements:

* address from which to accept connections
* port
* GUI startup flag

server.**config_load**()
    The function to load configuration parameters from an ini file. If the file does not exist, the default parameters are set.

core.py
~~~~~~~~~~~

..autoclass::server.core.MessageProcessor
    :members:

database.py
~~~~~~~~~~~

..autoclass::server.database.ServerStorage
    :members:

main_window.py
~~~~~~~~~~~~~~

..autoclass::server.main_window.MainWindow
    :members:

add_user.py
~~~~~~~~~~~

..autoclass::server.add_user.RegisterUser
    :members:

remove_user.py
~~~~~~~~~~~~~~

..autoclass::server.remove_user.DelUserDialog
    :members:

config_window.py
~~~~~~~~~~~~~~~~

..autoclass::server.config_window.ConfigWindow
    :members:

statistic_window.py
~~~~~~~~~~~~~~~~~~~

..autoclass::server.statistic_window.StatisticWindow
    :members: