import subprocess

PROCESSES = []


def main():
    while True:
        action = input(
            """Choose action:
            q - quit ,
            s - run server,
            k - run clients
            x - close all windows:""")
        match action:
            case "q":
                break
            case "s":
                PROCESSES.append(
                    subprocess.Popen(
                        "python server.py",
                        creationflags=subprocess.CREATE_NEW_CONSOLE))
            case "k":
                print("Make sure that the required number of clients "
                      "with a password of 123 are registered on the server.")
                print("The first start can be quite long due to "
                      "key generation!")
                clients_count = int(
                    input("Enter the number of test clients to run:"))
                for i in range(clients_count):
                    PROCESSES.append(
                        subprocess.Popen(
                            f"python client.py -n test{i + 1} -p 123",
                            creationflags=subprocess.CREATE_NEW_CONSOLE))
            case "x":
                while PROCESSES:
                    PROCESSES.pop().kill()


if __name__ == "__main__":
    main()
