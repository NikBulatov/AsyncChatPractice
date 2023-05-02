import json
from socket import socket, AF_INET, SOCK_STREAM
import sys


def get_client_msg(msg: bytes):
    return eval(msg.decode("utf-8"))


def parse_client_message(data: dict):
    try:
        if "action" in data.keys() and data["action"] == "presence" and "time" in data.keys() \
                and "user" in data.keys() and data["user"]["name"] == "Guest":
            return json.dumps({"response": 200})
        return json.dumps({
            "response": 400,
            "error": "Bad Request"
        })
    except KeyError:
        return json.dumps({
            "response": 400,
            "error": "Bad Request"
        })


def parse_arguments() -> dict:
    default_listen_ip_addr = ''
    default_port = 7777

    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = default_port
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        listen_port = default_port
    except ValueError:
        print('Server port is not valid')
        sys.exit(1)

    try:
        if '-i' in sys.argv:
            listen_ip_addr = sys.argv[sys.argv.index('-i') + 1]
        else:
            listen_ip_addr = default_listen_ip_addr

    except IndexError:
        print('Listen IP address is not valid')
        sys.exit(1)

    return {"ip_addr": listen_ip_addr, "port": listen_port}


def main():
    params = parse_arguments()

    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((
            params.get("ip_addr"),
            params.get("port")
        ))
        s.listen(2)

        while True:
            client, ip_addr = s.accept()
            data = client.recv(4096)
            try:
                client_msg = get_client_msg(data)
                response = parse_client_message(client_msg)
                client.send(response.encode("utf-8"))
            except BrokenPipeError:
                print("Internal error!")


if __name__ == "__main__":
    main()
