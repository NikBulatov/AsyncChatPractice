import getopt
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
    return json.load(data)


def process_answer(message: dict):
    if "response" in message.keys():
        if message["response"] == 200:
            return "200 : OK"
        return f"400 : {message['error']}"
    raise ValueError


def parse_arguments(argv: list) -> dict:
    arg_ip_addr = argv[1]
    arg_port = 7777
    arg_help = "{0} <server IP> [<server TCP port: 7777 default>]".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "h", ["help"])
        if not arg_ip_addr:
            raise ValueError("server IP is needed")
    except ValueError:
        print(arg_help)
        sys.exit(2)
    else:
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(arg_help)
                sys.exit(2)
        if argv[2]:
            arg_port = argv[2]
            if arg_port < 1024 or arg_port > 65535:
                arg_port = 7777
    finally:
        return {"ip_addr": arg_ip_addr, "port": arg_port}


def main():
    params = parse_arguments(sys.argv)
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
