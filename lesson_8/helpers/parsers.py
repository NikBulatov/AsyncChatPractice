import argparse
import sys
import logging
from .variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT
from .services import log, get_logger

LOGGER = get_logger()


@log
def _validate_port(listen_port: int) -> None:
    if not 1023 < listen_port < 65536:
        LOGGER.critical(
            f"Invalid port: {listen_port}. Allowed values: 1024 - 65535.")
        sys.exit(1)


@log
def parse_client_arguments() -> tuple:
    """
    Function to parse arguments from a command line.
    It returns tuple with passed ip address, port, mode

    :return: dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", default=DEFAULT_IP_ADDRESS, nargs="?")
    parser.add_argument("port", default=DEFAULT_PORT, type=int, nargs="?")
    parser.add_argument("-m", "--mode", default="listen", nargs="?")
    argspace = parser.parse_args(sys.argv[1:])
    server_address = argspace.addr
    server_port = argspace.port
    client_mode = argspace.mode

    _validate_port(server_port)

    if client_mode not in ("listen", "send"):
        LOGGER.critical(f"Invalid mode is specified {client_mode}, "
                        f"allowed modes: 'listen' , 'send'")
        sys.exit(1)

    return server_address, server_port, client_mode


@log
def parse_server_arguments() -> tuple:
    """
    Function to parse arguments from a command line.
    It returns tuple with passed ip address and port

    :return: dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", default=DEFAULT_PORT, type=int, nargs="?")
    parser.add_argument("-a", default="", nargs="?")
    argspace = parser.parse_args(sys.argv[1:])
    listen_address = argspace.a
    listen_port = argspace.p

    _validate_port(listen_port)

    return listen_address, listen_port
