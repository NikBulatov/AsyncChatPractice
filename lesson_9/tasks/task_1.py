import sys
from subprocess import Popen, PIPE
from socket import gethostbyname
from ipaddress import IPv4Address, ip_address
from platform import system
from typing import Iterable


def _ping(host, timeout: int = 250, amount: int = 1) -> Popen:
    """
    Ping command creator
    :param host:
    :param timeout:
    :param amount:
    :return:
    """
    param = '-n' if system().lower() == 'windows' else '-c'
    process = Popen(f"ping {host} -w {timeout} {param} {amount}", stdout=PIPE,
                    shell=False)
    return process


def _get_ip_addr(domain: str) -> str | IPv4Address:
    """
    Function parses received string containing IP address or domain name
    and returns string containing domain name or IPv4address object
    :param domain:
    :return:
    """
    try:
        ip_addr = ip_address(gethostbyname(domain))
    except (ValueError, TypeError):
        ip_addr = domain

    return ip_addr


def host_ping(endpoints: Iterable[str | IPv4Address]) -> dict:
    """
    Function receives a list of strings containing IP address,
    timeout connection and amount requests.
    It returns a dict with results of ping command
    :param endpoints:
    :return:
    """
    results = {"Reachable": [], "Unreachable": []}

    for addr in endpoints:
        host = _get_ip_addr(addr)
        process = _ping(host)
        process.wait()
        return_code = process.returncode
        match return_code:
            case 0:
                results["Reachable"] += [host]
                res_output = f"{host} - Узел доступен"
            case _:
                results["Unreachable"] += [host]
                res_output = f"{host} - Узел не доступен"
        print(res_output)
    return results


def main():
    ping_list = sys.argv[1:]
    host_ping(ping_list)


if __name__ == "__main__":
    main()
