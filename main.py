from socket import socket, AF_INET, SOCK_DGRAM
import pickle
import binascii
from time import time

cache = {}
cache_check_time = round(time())


def check_cache():
    if round(time()) - cache_check_time > 120:
        for name, _type in list(cache.keys()):
            for item in cache[(name, _type)]:
                if not item.can_live():
                    cache[(name, _type)].remove(item)


def parse_request(request):
    header = request[0:24]
    question = request[24:]



if __name__ == '__main__':
    try:
        with open("cache.txt", "rb") as f:
            cache = pickle.load(f)
    except FileNotFoundError:
        pass

    udp_socket = socket(AF_INET, SOCK_DGRAM)
    udp_socket.bind(('localhost', 53))

    # обработка сообщений в вечном цикле
    while True:
        received, address = udp_socket.recvfrom(4096)
        request = binascii.hexlify(received).decode("utf-8")

        request = parse_request(request)

        if request is not None:
            udp_socket.sendto(binascii.unhexlify(request), address)
        check_cache()
