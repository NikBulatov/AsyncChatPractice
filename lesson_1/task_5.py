"""
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet
"""

from subprocess import Popen, PIPE
from chardet import detect

YA_ARGS = ["ping", "-c", "4", "ya.ru"]
YOUTUBE_PING = ["ping", "-c", "4", "youtube.com"]

if __name__ == "__main__":
    with (Popen(YA_ARGS, stdout=PIPE) as YA_PING,
          Popen(YOUTUBE_PING, stdout=PIPE) as YOUTUBE_PING):
        for ya_line in YA_PING.stdout:
            ya_result = detect(ya_line)
            # print(ya_result)
            ya_line = ya_line.decode(ya_result.get("encoding")).encode()
            print(ya_line.decode())

        for you_line in YOUTUBE_PING.stdout:
            you_result = detect(you_line)
            # print(you_result)
            you_line = you_line.decode(you_result.get("encoding")).encode()
            print(you_line.decode())
