import subprocess

PROCESSES = []


def main():
    while True:
        action = input(f"""Выберите действие:
    q - выход;
    s - запустить сервер и клиенты;
    x - закрыть все окна: """)
        match action:
            case "q":
                break
            case "s":
                PROCESSES.append(
                    subprocess.Popen(
                        "python server.py",
                        creationflags=subprocess.CREATE_NEW_CONSOLE))
                for _ in range(2):
                    PROCESSES.append(
                        subprocess.Popen(
                            "python client.py -m send",
                            creationflags=subprocess.CREATE_NEW_CONSOLE))
                for _ in range(2):
                    PROCESSES.append(
                        subprocess.Popen(
                            "python client.py -m listen",
                            creationflags=subprocess.CREATE_NEW_CONSOLE))
            case "x":
                while PROCESSES:
                    victim = PROCESSES.pop()
                    victim.kill()


if __name__ == "__main__":
    main()
