Services package
================================================

A package of common utilities used in different project modules.

decos.py script
---------------

..automodule::services.decos
     :members:

descriptors.py script
---------------------

..autoclass::services.descryptors.Port
     :members:

errors.py script
---------------------

..autoclass::services.errors.IncorrectDataReceivedError
..autoclass::services.errors.ServerError
..autoclass::services.errors.NonDictionaryInputError
..autoclass::services.errors.RequiredFieldMissingError
    :members:

metaclasses.py script
----------------------

..autoclass::services.metaclasses.ServerVerifier
    :members:

..autoclass::services.metaclasses.ClientVerifier
    :members:

common.py script
---------------------

services.utils. **get_response** (client)


     The function of receiving messages from remote computers. Accepts JSON messages,
     decodes the received message and checks that a dictionary has been received.

services.utils. **send_request** (sock, message)


     Function for sending dictionaries via socket. Encodes a dictionary into JSON format and sends it over a socket.


variables.py script
---------------------

Contains various global project variables.