from socket import socket, AF_INET, SOCK_DGRAM
import pickle
import binascii
from time import time
from packetParser import Cache, get_name, parse_answer

cache_check_time = round(time())


def get_data_from_cache(key):
    data = cache.get(key)
    result = []
    count = 0
    for element in data:
        if element.can_live():
            result.append(element.__str__())
            count += 1
    return "".join(result), count


def check_cache(before_close=False):
    if round(time()) - cache_check_time > 60 or before_close:
        for name, _type in cache.keys():
            for item in cache.get((name, _type)):
                if not item.can_live():
                    cache.get((name, _type)).remove(item)
        with open("cache", "wb+") as file:
            pickle.dump(cache.cache, file)


def make_udp_request(request):
    message = request.replace(" ", "").replace("\n", "")
    sock = socket(AF_INET, SOCK_DGRAM)
    address = "77.88.8.1", 53
    sock.settimeout(1)
    try:
        sock.sendto(binascii.unhexlify(message), address)
        response, _ = sock.recvfrom(4096)
    except Exception:
        return None
    finally:
        sock.close()
    return binascii.hexlify(response).decode("utf-8")


def parse_request(request):
    if request is None:
        return None

    header = request[0:24]
    question = request[24:]

    name = get_name(question, 0, [])[0]
    _type = question[-8:-4]
    if cache.get((name, _type)) is not None:
        answer, count = get_data_from_cache((name, _type))
        if answer == "":
            answer_on_request = make_udp_request(request)
            if answer_on_request is not None:
                parse_answer(answer_on_request, cache)
            return answer_on_request
        _id = header[0:4]
        flags = "8180"
        questions_count = header[8:12]
        answers_count = hex(count)[2:].rjust(4, '0')
        ns_count = header[16:20]
        ar_count = header[20:24]
        new_header = _id + flags + questions_count + answers_count + ns_count + ar_count
        return new_header + question + answer
    answer_on_request = make_udp_request(request)
    if answer_on_request is not None:
        parse_answer(answer_on_request, cache)
        return answer_on_request
    return ""


if __name__ == '__main__':
    cache = Cache()
    try:
        with open("cache", "rb") as file:
            cache.cache = pickle.load(file)
    except FileNotFoundError:
        cache.cache = {}
    check_cache(True)
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    udp_socket.bind(('127.228.228.228', 53))

    while True:
        received, address = udp_socket.recvfrom(1024)
        request = binascii.hexlify(received).decode("utf-8")
        request = parse_request(request)
        if request is not None:
            udp_socket.sendto(binascii.unhexlify(request), address)
        check_cache()
