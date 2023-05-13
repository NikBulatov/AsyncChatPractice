import subprocess

PROCESS = []


def main():
    while True:
        ACTION = input(f"""Выберите действие:
            q - выход;
            s - запустить сервер и клиенты;
            x - закрыть все окна: """)
        match ACTION:
            case "q":
                break
            case "s":
                PROCESS.append(
                    subprocess.Popen(
                        "python server.py",
                        creationflags=subprocess.CREATE_NEW_CONSOLE))
                for _ in range(2):
                    PROCESS.append(
                        subprocess.Popen(
                            "python client.py -m send",
                            creationflags=subprocess.CREATE_NEW_CONSOLE))
                for _ in range(5):
                    PROCESS.append(
                        subprocess.Popen(
                            "python client.py -m listen",
                            creationflags=subprocess.CREATE_NEW_CONSOLE))
            case "x":
                while PROCESS:
                    VICTIM = PROCESS.pop()
                    VICTIM.kill()


if __name__ == "__main__":
    main()
