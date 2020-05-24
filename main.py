from socket import socket, AF_INET, SOCK_DGRAM
import pickle
import binascii
from zz.utils import decimal_to_hex
from time import time
from check import cache, get_name, parse_answer

cache_check_time = round(time())


def get_data_from_cache(key):
    data = cache[key]
    result = []
    count = 0
    for element in data:
        if element.can_live():
            result.append(element.__str__())
            count += 1
    return ".".join(result), count


def check_cache():
    if round(time()) - cache_check_time > 120:
        for name, _type in list(cache.keys()):
            for item in cache[(name, _type)]:
                if not item.can_live():
                    cache[(name, _type)].remove(item)


def make_udp_request(request):
    message = request.replace(" ", "").replace("\n", "")
    sock = socket(AF_INET, SOCK_DGRAM)
    address = "195.19.71.253", 53
    sock.settimeout(2)
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

    name = get_name(question, 0)[0]
    _type = question[-8:-4]
    if (name, _type) in cache:
        answer, count = get_data_from_cache((name, _type))
        if answer == "":
            answer_on_request = make_udp_request(request)
            if answer_on_request is not None:
                parse_answer(answer_on_request)
            return answer_on_request
        _id = header[0:4]
        flags = "8180"
        questions_count = header[8:12]
        answers_count = decimal_to_hex(count).rjust(4, '0')
        ns_count = header[16:20]
        ar_count = header[20:24]

        new_header = _id + flags + questions_count + answers_count + ns_count + ar_count
        return new_header + question + answer
    answer_on_request = make_udp_request(request)
    if answer_on_request is not None:
        parse_answer(answer_on_request)
    return answer_on_request


if __name__ == '__main__':
    # print(make_udp_request("0018010000010000000000000265310272750000010001"))
    answer = parse_answer("0018850000010001000200020265310272750000010001c00c000100010000012c0004c313dc0cc00c000200010000012c000a036e7331036e6773c00fc00c000200010000012c000b026e7305687364726ec00fc049000100010000003c0004c31347fdc0330001000100000e100004c313dcee")
    print(answer)
    print(answer)
    # try:
    #     with open("cache.txt", "rb") as f:
    #         cache = pickle.load(f)
    # except FileNotFoundError:
    #     pass
    #
    # udp_socket = socket(AF_INET, SOCK_DGRAM)
    # udp_socket.bind(('localhost', 53))
    #
    # # обработка сообщений в вечном цикле
    # while True:
    #     received, address = udp_socket.recvfrom(4096)
    #     request = binascii.hexlify(received).decode("utf-8")
    #     print(request)
    #
    #     request = parse_request(request)
    #     if request is not None:
    #         udp_socket.sendto(binascii.unhexlify(request), address)
    #     check_cache()
