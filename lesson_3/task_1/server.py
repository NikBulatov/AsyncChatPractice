import json
from socket import socket, AF_INET, SOCK_STREAM
import sys
import getopt


def get_client_msg(msg: bytes):
    return json.load(msg)


def parse_client_message(data: dict):
    if "action" in data.keys() and data["action"] == "presence" and "time" in data.keys() \
            and "user" in data.keys() and data["user"]["name"] == "Guest":
        return json.dumps({"response": 200})
    return json.dumps({
        "response": 400,
        "error": "Bad request"
    })


def parse_arguments(argv: list) -> dict:
    arg_ip_addr = ""
    arg_port = 7777
    arg_help = "{0} -a <listened IP: default all IPs listened> -p <TCP port: 7777 default>".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "ha:p:", ["help", "ip_addr=", "port="])
    except Exception:
        print(arg_help)
        sys.exit(2)
    else:
        for opt, arg in opts:
            match opt:
                case "-h" | "--help":
                    print(arg_help)
                    sys.exit(2)
                case "-a" | "--ip_addr":
                    arg_ip_addr = arg
                case "-p" | "--port":
                    if int(arg) < 1024 or int(arg) > 65535:
                        arg_port = 7777
                    else:
                        arg_port = arg
    finally:
        return {"ip_addr": arg_ip_addr, "port": arg_port}


def main():
    params = parse_arguments(sys.argv)

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
            except Exception:
                print("Pizdec!")


if __name__ == "__main__":
    main()
