import json
from socket import socket, AF_INET, SOCK_STREAM
import sys
import time


def create_presence(account_name='Guest'):
    message = {
        "action": "presence",
        "time": time.time(),
        "user": {
            "name": account_name
        }
    }
    return json.dumps(message)


def get_message(data: bytes):
    return eval(data.decode("utf-8"))


def process_answer(message: dict):
    if "response" in message.keys():
        if message["response"] == 200:
            return "200 : OK"
        return f"400 : {message['error']}"
    raise ValueError


def parse_arguments() -> dict:
    default_server_ip_addr = '127.0.0.1'
    default_server_port = 7777

    try:
        server_ip_addr = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError("Server port is not valid")
    except IndexError:
        server_ip_addr = default_server_ip_addr
        server_port = default_server_port
    except ValueError:
        sys.exit(2)

    return {"ip_addr": server_ip_addr, "port": server_port}


def main():
    params = parse_arguments()
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((
            params.get("ip_addr"),
            params.get("port")
        ))

        msg = create_presence()
        s.send(msg.encode("utf-8"))
        data = s.recv(4096)
        try:
            answer = process_answer(get_message(data))
            print(answer)
        except (ValueError, json.JSONDecodeError):
            print('Не удалось декодировать сообщение сервера.')


if __name__ == "__main__":
    main()
