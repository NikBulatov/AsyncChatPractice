import sys
from subprocess import Popen, CREATE_NEW_CONSOLE


def main(amount: int):
    PROCESSES = []
    while True:
        action = input(f"""Actions:
    q - quit;
    r - run a server and {amount} clients;
    t - terminate all consoles:\n\r""")
        match action:
            case "q":
                break
            case "r":
                PROCESSES.append(Popen("python server.py",
                                       creationflags=CREATE_NEW_CONSOLE))
                for i in range(amount):
                    PROCESSES.append(Popen(f"python client.py -n user_{i}",
                                           creationflags=CREATE_NEW_CONSOLE))
            case "t":
                while PROCESSES:
                    victim = PROCESSES.pop()
                    victim.kill()


if __name__ == "__main__":
    main(int(sys.argv[1]))
