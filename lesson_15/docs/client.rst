Client module
=================================================

Messaging client application. Supports sending messages to users who are online, messages are encrypted using the RSA algorithm with a key length of 2048 bit.

Supports command line arguments:

```python client.py {server host} {port} -n ot --name {username} -p или --password {password}```

1. {server host} - messages server ip address.
2. {port} - listening port on which connections are accepted
3. -n or --name - username to login.
4. -p or --password - username password.

All CML arguments are optional, but the username and password must be used

Examples:

* ``python client.py``

*Launching the application with default settings*

* ``python client.py ip_address some_port``

*Launching the application with instructions to connect to the server at ip_address:port*

* ``python -n test1 -p 123``

*Running application with user test1 and password 123*

* ``python client.py ip_address some_port -n test1 -p 123``

*Launching the application with the user test1 and password 123 and specifying to connect to the server at ip_address:port*

client.py
~~~~~~~~~

A executable module that contains a command line argument parser and application initialization functionality.

client. **parse_client_args** ()
    Command line argument parser, returns a tuple of 4 elements:
    
    * server ip address
    * port
    * username
    * password

    Performs validation of the port number.


client_models.py
~~~~~~~~~~~~~~~~

.. autoclass:: client.database.ClientDatabase
    :members:

transport.py
~~~~~~~~~~~~~~

.. autoclass:: client.transport.ClientTransport
    :members:

main_window.py
~~~~~~~~~~~~~~

.. autoclass:: client.main_window.ClientMainWindow
    :members:

start_dialog.py
~~~~~~~~~~~~~~~

.. autoclass:: client.start_dialog.UserNameDialog
    :members:


add_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.add_contact.AddContactDialog
    :members:


del_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.del_contact.DelContactDialog
    :members: