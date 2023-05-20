import re
import ipaddress
from pprint import pprint
from task_1 import host_ping


def _validate_string(value: str) -> bool:
    """
    Validate a string using regex
    :param value:
    :return:
    """
    pattern = re.compile(r"^((\d{1,3}\.){3}\d{1,3})$")
    return bool(pattern.match(value))


def host_range_ping(first_addr: str, amount: int) -> dict:
    """
    Function sorts ip addresses from a received range.
    It changes the last octet of ip address and print results.
    :param first_addr:
    :param amount:
    :return:
    """
    if _validate_string(first_addr):
        last_octet = int(first_addr.split('.')[-1])
        if (last_octet + amount) < 254:
            result = host_ping(
                [ipaddress.ip_address(first_addr) + i for i in range(amount)])
            return result
        else:
            raise ValueError("Invalid amount of addresses")
    else:
        raise ValueError("Invalid string received")


def main():
    results = host_range_ping("192.168.0.1", 15)
    pprint(results)


if __name__ == "__main__":
    main()
