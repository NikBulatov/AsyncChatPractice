from subprocess import Popen, PIPE

FILE_PATH = "test_file.txt"

if __name__ == "__main__":
    with (open(FILE_PATH, "r") as file,
          Popen(["file", "-bi", FILE_PATH], stdout=PIPE) as cmd_result):
        encoding_file = "".join([line.decode() for line in cmd_result.stdout]).split()[-1]
        print(f"file's {encoding_file}")
        lines = [line.strip() for line in file.readlines()]
        print(*lines)
