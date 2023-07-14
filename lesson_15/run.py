from subprocess import Popen, CREATE_NEW_CONSOLE


def main():
    PROCESSES = []
    while True:
        action = input(
            """Actions:
    q - quit;
    r - run server and clients;
    t - terminate all consoles:\n\r"""
        )
        match action:
            case "q":
                break
            case "r":
                PROCESSES.append(
                    Popen("python core.py", creationflags=CREATE_NEW_CONSOLE)
                )
                for i in range(1, 3):
                    PROCESSES.append(
                        Popen(
                            f"python client.py -n user_{i}",
                            creationflags=CREATE_NEW_CONSOLE,
                        )
                    )
            case "t":
                while PROCESSES:
                    victim = PROCESSES.pop()
                    victim.kill()


if __name__ == "__main__":
    main()
