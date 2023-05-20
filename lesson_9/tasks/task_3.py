from tabulate import tabulate
from task_2 import host_range_ping


def host_range_ping_tab(first_addr, amount):
    """
    Function print a table with reachable and unreachable hosts.
    It takes first ip address and amount of addresses to check
    :param first_addr:
    :param amount:
    :return:
    """

    result = host_range_ping(first_addr, amount)
    print(
        tabulate(result, headers="keys", tablefmt="pipe", stralign="center"))


def main():
    host_range_ping_tab("10.45.0.1", 35)


if __name__ == "__main__":
    main()
