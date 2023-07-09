import argparse
import sys
import logging
from .variables import DEFAULT_PORT
from .common import log, get_logger

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
    parser.add_argument("addr", default="127.0.0.1", nargs="?")
    parser.add_argument("port", default=DEFAULT_PORT, type=int, nargs="?")
    parser.add_argument("-n", "--name", default=None, nargs="?")
    argspace = parser.parse_args(sys.argv[1:])
    server_address = argspace.addr
    server_port = argspace.port
    account_name = argspace.name

    _validate_port(server_port)

    return server_address, server_port, account_name


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
