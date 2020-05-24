import socket
import binascii
from packetStrucrures import *

cache = {}


# def send_udp_message(message, ip, port):
#     message = message.replace(" ", "").replace("\n", "")
#     server_address = (ip, port)
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.sendto(binascii.unhexlify(message), server_address)
#     data, address = sock.recvfrom(1024)
#     sock.close()
#     res = data.hex()
#     return res


def format_hex(hex):
    """format_hex returns a pretty version of a hex string"""
    octets = [hex[i:i + 2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i + 2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)


def format_name(domains):
    results = []
    for d in domains:
        res = []
        for domain in d:
            pairs = [int(domain[i:i + 2], 16) for i in range(0, len(domain), 2)]
            res.append("".join([chr(i) for i in pairs]))
        results.append(".".join(res))
    return results


# def parse_flags(flags):
#     bin_number = bin(int(flags, 16))[2:]
#     _response = bin_number[0]
#     aa = bin_number[5]
#     recursion_desired = bin_number[7]
#     recursion_available = bin_number[8]
#     reply_code = bin_number[12:]
#     return Flags(_response, aa, recursion_desired, recursion_available, reply_code)


def take_standart_mark(domain_len, answer, start_pos):
    domain = ""
    for i in range(domain_len * 2):
        domain += answer[start_pos + 2 + i]
    return domain


def input_rd_data(_bytes, rd_len):
    result = []
    b = ""
    for i in range(rd_len * 2):
        b += _bytes[i]
        if i % 2 == 1:
            result.append(str(int(b, 16)))
            b = ""
    return ".".join(result)


def find_domain_names(answer, start_pos, domains, counter, domain, stop):
    t = answer[start_pos:start_pos + 2]
    domain_len = int(answer[start_pos:start_pos + 2], 16)
    if 64 > domain_len > 0:
        domain.append(take_standart_mark(domain_len, answer, start_pos))
        j = start_pos + 2 + domain_len * 2
        if answer[j:j + 2] == "00":
            counter -= 1
            domains.append(domain)
            domain = []
            stop = True
        start_pos = start_pos + 2 + domain_len * 2
    elif domain_len >= 64:
        t = answer[start_pos:start_pos + 4]
        pos = (int(answer[start_pos:start_pos + 4], 16) - 49152) * 2
        previous_name_len = int(answer[pos * 2:pos * 2 + 2], 16)
        c = ""
        while pos < start_pos - 2:
            c = answer[pos:pos + 2]
            domain_len = int(answer[pos:pos + 2], 16)
            a = take_standart_mark(domain_len, answer, pos)
            if a != "":
                domain.append(a)
            else:
                stop = True
                break
            pos += domain_len * 2 + 2
        counter -= 1
        domains.append(domain)
        domain = []
        start_pos += 4
    else:
        start_pos += 2
    return start_pos, domains, counter, domain, stop


def get_name(answer, start_pos, domains=[]):
    domain = []
    stop = False
    while not stop:
        start_pos, domains, i, domain, stop = find_domain_names(answer, start_pos, domains, 1, domain, stop)
    return format_name(domains)


def parse_answer(answer):
    id = answer[:4]
    # flags_data = answer[4:8]
    # flags = parse_flags(flags_data)
    questions = int(answer[8:12], 16)  # число запросов
    answer_rrs = int(answer[12:16], 16)
    authority_rrs = int(answer[16:20], 16)
    additional_rrs = int(answer[20:24], 16)
    # header = Header(id, flags, questions, answer_rrs, authority_rrs, additional_rrs)
    start_pos = 24
    domains = []
    i = questions
    domain = []
    while i > 0:
        start_pos, domains, i, domain, _ = find_domain_names(answer, start_pos, domains, i, domain, True)
    name = format_name(domains)
    # q_type = int(answer[start_pos + 2:start_pos + 6], 16)
    # q_class = int(answer[start_pos + 6:start_pos + 10], 16)
    # query = Query(name, q_type, q_class)
    # query = answer[24:start_pos + 10]
    stop = False
    domains = []
    j = answer_rrs
    start_pos += 14

    answers = []
    while j > 0:
        s_p = start_pos - 4
        pos = (int(answer[start_pos - 4:start_pos], 16) - 49152) * 2
        while not stop:
            pos, domains, i, domain, stop = find_domain_names(answer, pos, domains, 1, domain, stop)
        name = format_name(domains)[0]
        _type = int(answer[start_pos:start_pos + 4], 16)
        # _class = int(answer[start_pos + 4:start_pos + 8], 16)
        ttl = int(answer[start_pos + 12:start_pos + 16], 16)
        rd_length = int(answer[start_pos + 16:start_pos + 20], 16) * 2
        # rd_data = input_rd_data(answer[start_pos + 20:start_pos + 20 + rd_length * 2], rd_length)
        data = answer[start_pos + 16:start_pos + 20 + rd_length]
        answ = Answer(name, _type, ttl, data)
        if cache.get((name, _type), None) is None:
            cache[(name, _type)] = [answ]
        else:
            cache[(name, _type)].append(answ)
        answers.append(NewStrc(_type, ttl, data))
        start_pos += 24 + rd_length
        j -= 1
    j = authority_rrs
    stop = False
    author_servers = []
    domains = []
    while j > 0:
        # print(answer[start_pos - 4:start_pos])
        pos = (int(answer[start_pos - 4:start_pos], 16) - 49152) * 2
        # print(pos)
        while not stop:
            pos, domains, i, domain, stop = find_domain_names(answer, pos, domains, 1, domain, stop)

        name = format_name(domains)[0]
        # print(name)
        # print(answer[start_pos:start_pos + 4])
        _type = int(answer[start_pos:start_pos + 4], 16)
        # _class = int(answer[start_pos + 4:start_pos + 8], 16)
        ttl = int(answer[start_pos + 12:start_pos + 16], 16)
        data_length = int(answer[start_pos + 16:start_pos + 20], 16) * 2
        # cur_pos = start_pos + 20
        # result, cur_pos = find_mailbox_or_name_server(answer, cur_pos)
        # server_name = format_name([result[0]])
        # mailbox, cur_pos = find_mailbox_or_name_server(answer, cur_pos)
        # mailbox = format_name([mailbox[0]])
        # serial_number = int(answer[cur_pos:cur_pos + 8], 16)
        # refresh_interval = int(answer[cur_pos + 8:cur_pos + 16], 16)
        # retry_interval = int(answer[cur_pos + 16:cur_pos + 24], 16)
        # expire_limit = int(answer[cur_pos + 24:cur_pos + 32], 16)
        # minimum_ttl = int(answer[cur_pos + 32:cur_pos + 40], 16)
        data = answer[start_pos + 16:start_pos + 20 + data_length]
        # print(data)
        ans = NewStrc(_type, ttl, data)
        # print((name, _type))
        if cache.get((name, _type), None) is None:
            cache[(name, _type)] = [ans]
        else:
            cache[(name, _type)].append(ans)
        j -= 1

        start_pos += 24 + data_length
        t = answer[start_pos:start_pos + 4]
    j = additional_rrs
    additional_records = []
    while j > 0:
        t = answer[start_pos - 4:start_pos]
        result, start_pos = find_mailbox_or_name_server(answer, start_pos - 4)
        name = format_name([result[0]])[0]
        _type = int(answer[start_pos:start_pos + 4], 16)
        ttl = int(answer[start_pos + 8:start_pos + 16], 16)
        data_length = int(answer[start_pos + 16:start_pos + 20], 16) * 2
        data = answer[start_pos + 16:start_pos + 20 + data_length]
        ar = NewStrc(_type, ttl, data)
        if cache.get((name, _type), None) is None:
            cache[(name, _type)] = [ar]
        else:
            cache[(name, _type)].append(ar)
        # additional_records.append(AdditionalRecords(name, _type, ttl, data))
        start_pos += 24 + data_length
        j -= 1
    # cache_info = CacheInfo(answers, author_servers, additional_records)
    print(1)


def find_mailbox_or_name_server(answer, start_pos):
    result = []
    domain = []
    domains = []
    stop = False
    while True:
        t = answer[start_pos:start_pos + 2]
        domain_len = int(answer[start_pos:start_pos + 2], 16)
        if 64 > domain_len > 0:
            domain.append(take_standart_mark(domain_len, answer, start_pos))
            j = start_pos + 2 + domain_len * 2
            result.append(domain)
            start_pos = start_pos + 2 + domain_len * 2
            if answer[j:j + 2] == "00":
                start_pos += 2
                break
        elif domain_len >= 64:
            t = answer[start_pos:start_pos + 4]
            pos = (int(answer[start_pos:start_pos + 4], 16) - 49152) * 2
            while answer[pos:pos + 2] != "00" and not stop:
                pos, domains, _, domain, stop = find_domain_names(answer, pos, domains, 1, domain, stop)
            for d in domains:
                result.append(d)
            start_pos += 4
            break
    return result, start_pos


def parse_response(response):
    header = response[0:24]
    question = response[24:]
    transaction_id = int(header[0:4], 16)
