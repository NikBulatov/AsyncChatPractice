import sys
from subprocess import Popen, PIPE
from socket import gethostbyname
from ipaddress import IPv4Address, ip_address
from platform import system


def get_ip_addr(domain: str) -> str | IPv4Address:
    """
    Function parses received string containing IP address or domain name
    and returns string containing domain name or IPv4address object
    :param domain:
    :return:
    """
    try:
        ip_addr = ip_address(gethostbyname(domain))
    except ValueError:
        ip_addr = domain

    return ip_addr


def host_ping(endpoints: list[str], timeout: int = 500,
              amount: int = 1) -> dict:
    """
    Function receives a list of strings containing IP address,
    timeout connection and amount requests.
    It returns a dict with results of ping command
    :param endpoints:
    :param timeout:
    :param amount:
    :return:
    """
    results = {0: "", 1: ""}

    param = '-n' if system().lower() == 'windows' else '-c'
    for addr in endpoints:
        if isinstance(addr, str):
            host = get_ip_addr(addr)
            command = f"ping {host} -w {timeout} {param} {amount}"
            process = Popen(command, stdout=PIPE)
            process.wait()

            if process.returncode == 0:
                results[0] += f"{addr}\n"
                res_output = f"{addr} - Узел доступен"
            else:
                results[1] += f"{addr}\n"
                res_output = f"{addr} - Узел не доступен"
            print(res_output)
    return results


def main():
    ping_list = sys.argv[1:]
    host_ping(ping_list)


if __name__ == "__main__":
    main()
