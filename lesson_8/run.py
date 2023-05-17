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
                for i in range(1, 3):
                    PROCESSES.append(
                        subprocess.Popen(
                            f"python client.py -n user_{i}",
                            creationflags=subprocess.CREATE_NEW_CONSOLE))
            case "x":
                while PROCESSES:
                    victim = PROCESSES.pop()
                    victim.kill()


if __name__ == "__main__":
    main()
