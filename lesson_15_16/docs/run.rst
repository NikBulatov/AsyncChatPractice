Run module
================================================

Module to run multiple clients at the same time.

Usage:

After launch, you will be prompted to enter a command.
Supported commands:

1.s - Start server

* Starts the server with default settings.

2. k - Run clients

* You will be prompted for the number of test clients to run.
* Clients will be launched with names like **test1 - testX** and passwords **123**
* Test users must first manually register on the server with the password **123**.
* If the clients are being launched for the first time, the startup time may be quite long due to the generation of new RSA keys.

3. x - Close all windows
 
* Closes all active windows that were launched from this module.
 
4. q - Shut down the module
 
* Ends the module