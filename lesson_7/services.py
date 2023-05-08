import json
import socket
import time

from variables import (ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS,
                       PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, ENCODING,
                       MAX_PACKAGE_LENGTH, DEFAULT_IP_ADDRESS)
import inspect
import sys
import logging
from builtins import callable
from functools import wraps

if sys.argv[0].find("client") == -1:
    LOGGER = logging.getLogger("server")
else:
    LOGGER = logging.getLogger("client")


def log(func: callable) -> callable:
    """
    Decorator for logging when and where decorated function was called
    :param func: callable
    :return: callable
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        LOGGER.debug(
            f"\"{func.__name__}\" function with arguments {args}, {kwargs} "
            f"was called from \"{inspect.stack()[1][3]}\" function, "
            f"from module {func.__module__}")
        return result

    return wrapper


@log
def create_presence(account_name="Guest") -> dict:
    """
    Function to create a presence message with the given account name

    :param account_name: str
    :return: dict
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f"Message:{PRESENCE} is ready for user: {account_name}")
    return out


@log
def init_listen_socket(sock_pair: tuple,
                       count_listen_to: int = MAX_CONNECTIONS,
                       timeout: float = 0.2) -> socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(sock_pair)
    sock.listen(count_listen_to)
    sock.settimeout(timeout)
    return sock


@log
def process_client_message(message) -> dict:
    """
    Function to process a client message and return response.

    :param message:
    :return response: dict
    """
    LOGGER.debug(f"Parse client message {message}")
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == "Guest":
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: "Bad Request"
    }


@log
def parse_client_arguments() -> tuple:
    """
    Function to parse arguments from a command line.
    It returns tuple with passed ip address and port

    :return: dict
    """
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            LOGGER.critical(
                f"Invalid port number: {server_port}. Client closed!")
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print("Invalid port number")
        sys.exit(1)

    return server_address, server_port


@log
def parse_server_arguments() -> tuple:
    """
    Function to parse arguments from a command line.
    It returns tuple with passed ip address and port

    :return: dict
    """
    try:
        if "-p" in sys.argv:
            listen_port = int(sys.argv[sys.argv.index("-p") + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print("Port needed")
        LOGGER.critical("Listening port was not passed!")
        sys.exit(1)
    except ValueError:
        print("Invalid port value")
        LOGGER.critical("Invalid listening port passed!")
        sys.exit(1)

    try:
        if "-a" in sys.argv:
            listen_address = int(sys.argv[sys.argv.index("-a") + 1])
        else:
            listen_address = ""

    except IndexError:
        print("IP address needed")
        LOGGER.critical("Invalid listening IP address passed!")
        sys.exit(1)

    return listen_address, listen_port


def read_requests(r_clients: list, all_clients: list) -> dict:
    """
    Read requests by connected clients
    :param r_clients:
    :param all_clients:
    :return:
    """
    responses = {}  # Словарь ответов сервера вида {сокет: запрос}
    for sock in r_clients:
        try:
            data = sock.recv(1024).decode('utf-8')
            responses[sock] = data
        except Exception as e:
            print(e,
                  f'\nClient {sock.fileno()} {sock.getpeername()} closed connection')
            all_clients.remove(sock)
    return responses


def write_responses(requests: dict, w_clients: list, all_clients: list) -> None:
    """
    Echo-response by server to client
    :param requests:
    :param w_clients:
    :param all_clients:
    :return:
    """
    for sock in w_clients:
        if sock in requests:
            try:
                resp = requests[sock].encode('utf-8')
                # Эхо-ответ сделаем чуть непохожим на оригинал
                sock.send(resp.upper())
            except Exception as e:  # Сокет недоступен, клиент отключился
                print(f'Client {sock.fileno()} {sock.getpeername()} closed connection')
                sock.close()
                all_clients.remove(sock)


def get_message(client: socket) -> dict:
    """
    Function to retrieve a message

    :param client: socket
    :return: dict
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock: socket, message) -> None:
    """
    Function to send a message

    :param sock: socket
    :param message:
    :return:
    """
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)


@log
def process_answer(message) -> str:
    """
    Function to return an answer message

    :param message: str
    :return: str
    """
    LOGGER.debug(f"Parse server message: {message}")
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return "200 : OK"
        return f"400 : {message[ERROR]}"
    raise ValueError
