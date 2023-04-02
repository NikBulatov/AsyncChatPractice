"""
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet
"""

from subprocess import Popen, PIPE

YA_ARGS = ["ping", "-c", "4", "ya.ru"]
YOUTUBE_PING = ["ping", "-c", "4", "youtube.com"]
with (Popen(YA_ARGS, stdout=PIPE) as YA_PING,
      Popen(YOUTUBE_PING, stdout=PIPE) as YOUTUBE_PING):
    for ya_line in YA_PING.stdout:
        print(ya_line)
        print(ya_line.decode())
    print()
    for youtube_line in YOUTUBE_PING.stdout:
        print(youtube_line)
        print(youtube_line.decode())

# b'PING ya.ru (5.255.255.242) 56(84) bytes of data.\n'
# b'64 bytes from ya.ru (5.255.255.242): icmp_seq=1 ttl=245 time=17.5 ms\n'
# b'64 bytes from ya.ru (5.255.255.242): icmp_seq=2 ttl=245 time=16.4 ms\n'
# b'64 bytes from ya.ru (5.255.255.242): icmp_seq=3 ttl=245 time=17.6 ms\n'
# b'64 bytes from ya.ru (5.255.255.242): icmp_seq=4 ttl=245 time=17.3 ms\n'
# b'\n'
# b'--- ya.ru ping statistics ---\n'
# b'4 packets transmitted, 4 received, 0% packet loss, time 3004ms\n'
# b'rtt min/avg/max/mdev = 16.368/17.185/17.564/0.479 ms\n'
#
# b'PING youtube.com (216.58.210.174) 56(84) bytes of data.\n'
# b'64 bytes from hem08s07-in-f14.1e100.net (216.58.210.174): icmp_seq=1 ttl=56 time=46.6 ms\n'
# b'64 bytes from hem08s07-in-f14.1e100.net (216.58.210.174): icmp_seq=2 ttl=56 time=45.7 ms\n'
# b'64 bytes from hem08s07-in-f14.1e100.net (216.58.210.174): icmp_seq=3 ttl=56 time=47.9 ms\n'
# b'64 bytes from hem08s07-in-f14.1e100.net (216.58.210.174): icmp_seq=4 ttl=56 time=46.9 ms\n'
# b'\n'
# b'--- youtube.com ping statistics ---\n'
# b'4 packets transmitted, 4 received, 0% packet loss, time 3001ms\n'
# b'rtt min/avg/max/mdev = 45.661/46.765/47.937/0.813 ms\n'


# PING ya.ru (213.180.193.1) 56(84) bytes of data.
# 64 bytes from ns1.yandex.net (213.180.193.1): icmp_seq=1 ttl=54 time=17.2 ms
# 64 bytes from ns1.yandex.net (213.180.193.1): icmp_seq=2 ttl=54 time=15.8 ms
# 64 bytes from ns1.yandex.net (213.180.193.1): icmp_seq=3 ttl=54 time=21.7 ms
# 64 bytes from ns1.yandex.net (213.180.193.1): icmp_seq=4 ttl=54 time=16.0 ms
#
# --- ya.ru ping statistics ---
# 4 packets transmitted, 4 received, 0% packet loss, time 3005ms
# rtt min/avg/max/mdev = 15.794/17.668/21.697/2.382 ms
#
#
# PING youtube.com (216.239.32.10) 56(84) bytes of data.
# 64 bytes from ns1.google.com (216.239.32.10): icmp_seq=1 ttl=101 time=56.2 ms
# 64 bytes from ns1.google.com (216.239.32.10): icmp_seq=2 ttl=101 time=54.6 ms
# 64 bytes from ns1.google.com (216.239.32.10): icmp_seq=3 ttl=101 time=54.8 ms
# 64 bytes from ns1.google.com (216.239.32.10): icmp_seq=4 ttl=101 time=54.9 ms
#
# --- youtube.com ping statistics ---
# 4 packets transmitted, 4 received, 0% packet loss, time 3004ms
# rtt min/avg/max/mdev = 54.635/55.152/56.224/0.628 ms
