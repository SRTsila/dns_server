import socket
import binascii
from beaker import cache
import time


class AuthoritativeNameServer:
    def __init__(self, name, _type, _class, ttl, data_length, name_server):
        self.name = name
        self._type = _type
        self._class = _class
        self.ttl = ttl
        self.data_length = data_length
        self.name_server = name_server


class DNSPacket:
    def __init__(self, header, query, answers=None, authority_rrs=None, additional_rrs=None):
        self.answers = answers
        self.header = header
        self.query = query
        self.authority_rrs = authority_rrs
        self.additional_rrs = additional_rrs


class Answer:
    def __init__(self, name, _type, _class, ttl, data_length, address):
        self.name = name
        self._type = _type
        self._class = _class
        self.ttl = ttl
        self.data_length = data_length
        self.address = address


class Flags:
    def __init__(self, qr, aa, recursion_desired, recursion_available, error_code):
        self.qr = qr
        self.aa = aa
        self.recursion_desired = recursion_desired
        self.recursion_available = recursion_available
        self.reply_code = error_code


class Header:
    def __init__(self, id, flags: Flags, request_number, answer_count, ns_count, ar_count):
        self.id = id
        self.flags = flags
        self.request_number = request_number
        self.answer_count = answer_count
        self.ns_count = ns_count
        self.ar_count = ar_count


class Query:
    def __init__(self, domains, q_type, q_class):
        self.domains = domains
        self.q_type = q_type
        self.q_class = q_class


def send_udp_message(message, ip, port):
    message = message.replace(" ", "").replace("\n", "")
    server_address = (ip, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(binascii.unhexlify(message), server_address)
    data, address = sock.recvfrom(1024)
    sock.close()
    res = data.hex()
    return res


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


def parse_flags(flags):
    bin_number = bin(int(flags, 16))[2:]
    _response = bin_number[0]
    aa = bin_number[5]
    recursion_desired = bin_number[7]
    recursion_available = bin_number[8]
    reply_code = bin_number[12:]
    return Flags(_response, aa, recursion_desired, recursion_available, reply_code)


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
        pos = int(answer[start_pos:start_pos + 4], 16) - 49152
        while pos < start_pos - 2:
            c = answer[pos:pos + 2]
            domain_len = int(answer[pos:pos + 2], 16)
            domain.append(take_standart_mark(domain_len, answer, pos))
            pos += domain_len * 2 + 2
        counter -= 1
        domains.append(domain)
        domain = []
        start_pos += 4
    else:
        start_pos += 2
    return start_pos, domains, counter, domain, stop


def answer_parser(answer):
    id = answer[:4]
    flags_data = answer[4:8]
    flags = parse_flags(flags_data)
    questions = int(answer[8:12], 16)  # число запросов
    answer_rrs = int(answer[12:16], 16)
    authority_rrs = int(answer[16:20], 16)
    additional_rrs = int(answer[20:24], 16)
    header = Header(id, flags, questions, answer_rrs, authority_rrs, additional_rrs)
    start_pos = 24
    domains = []
    i = questions
    domain = []
    while i > 0:
        start_pos, domains, i, domain, _ = find_domain_names(answer, start_pos, domains, i, domain, True)
    name = format_name(domains)
    q_type = int(answer[start_pos + 2:start_pos + 6], 16)
    q_class = int(answer[start_pos + 6:start_pos + 10], 16)
    quiry = Query(name, q_type, q_class)
    stop = False
    domains = []
    j = answer_rrs
    start_pos += 14
    answers = []
    while j > 0:
        pos = (int(answer[start_pos - 4:start_pos], 16) - 49152) * 2
        while not stop:
            pos, domains, i, domain, stop = find_domain_names(answer, pos, domains, 1, domain, stop)
        name = format_name(domains)
        _type = int(answer[start_pos:start_pos + 4], 16)
        _class = int(answer[start_pos + 4:start_pos + 8], 16)
        ttl = int(answer[start_pos + 12:start_pos + 16], 16)
        rd_length = int(answer[start_pos + 16:start_pos + 20], 16)
        rd_data = input_rd_data(answer[start_pos + 20:start_pos + 20 + rd_length * 2], rd_length)
        answers.append(Answer(name, _type, _class, ttl, rd_length, rd_data))
        start_pos += 24 + rd_length * 2
        j -= 1
    x = DNSPacket(header, quiry, answers)
    j = authority_rrs
    stop = False
    author_servers = []
    domains = []
    d = []
    while j > 0:
        pos = (int(answer[start_pos - 4:start_pos], 16) - 49152) * 2
        while not stop:
            pos, domains, i, domain, stop = find_domain_names(answer, pos, domains, 1, domain, stop)
        name = format_name(domains)
        _type = int(answer[start_pos:start_pos + 4], 16)
        _class = int(answer[start_pos + 4:start_pos + 8], 16)
        ttl = int(answer[start_pos + 12:start_pos + 16], 16)
        data_length = int(answer[start_pos + 16:start_pos + 20], 16)
        cur_pos = start_pos + 20
        while cur_pos < start_pos + 21 + data_length*2:
            cur_pos, d, _, domain, __ = find_domain_names(answer, cur_pos, d, 1, domain, False)
            t = answer[cur_pos-1:cur_pos+1]
        r = [domain]
        server_name = format_name(r)
        print(server_name)
        author_servers.append(AuthoritativeNameServer(name, _type, _class, ttl, data_length, server_name))
        j -= 1


message = "aa bb 01 00 00 01 00 00 00 00 00 00 " \
          "07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00 01"

# response = "aabb81800002000100000000076578616d706c6503636f6d00c0180000010001c00c00010001000006e600045db8d822"
# response = "00 02 81 80 00 01 00 02 00 00 00 00 09 77 69 6b 69 70 65 64 69 61 02 72 75 00 00 01 00 01 c0 0c 00 01 00 01 00 00 0c ce 00 04 5b c3 f0 7e c0 0c 00 01 00 01 00 00 0c ce 00 04 5b c3 f0 87"
# response = send_udp_message(message, "8.8.8.8", 53)
# print(format_hex(response.replace(" ", "")))
response = "0002850000010001000200020265310272750000010001c00c000100010000012c0004c313dc0cc00c000200010000012c000b026e7305687364726ec00fc00c000200010000012c000a036e7331036e6773c00fc033000100010000003c0004c31347fdc04a0001000100000e100004c3e2de41"
answer_parser(response.replace(" ", ''))
