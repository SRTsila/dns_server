import socket
import binascii
from beaker import cache
import time


class Flags:
    def __init__(self, qr, aa, rd, ra, rcode):
        self.qr = qr
        self.aa = aa
        self.rd = rd
        self.ra = ra
        self.rcode = rcode


class Header:
    def __init__(self, id, flags: Flags, request_number, answer_count, ns_count, ar_count):
        self.id = id
        self.flags = flags
        self.request_number = request_number
        self.answer_count = answer_count
        self.ns_count = ns_count
        self.ar_count = ar_count


class Request:
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
    print(res)
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
    qr = bin_number[0]
    aa = bin_number[5]
    rd = bin_number[7]
    ra = bin_number[8]
    rcode = bin_number[12:]
    return Flags(qr, aa, rd, ra, rcode)


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
    global start_pos
    id = answer[:4]
    flags_data = answer[4:8]
    flags = parse_flags(flags_data)
    re_count = int(answer[8:12], 16)  # число запросов
    an_count = int(answer[12:16], 16)
    ns_count = int(answer[16:20], 16)
    ar_count = int(answer[20:24], 16)
    header = Header(id, flags, re_count, an_count, ns_count, ar_count)
    start_pos = 24
    domains = []
    i = re_count
    domain = []
    while i > 0:
        start_pos, domains, i, domain, _ = find_domain_names(answer, start_pos, domains, i, domain, True)
    name = format_name(domains)
    q_type = int(answer[start_pos + 2:start_pos + 6], 16)
    q_class = int(answer[start_pos + 6:start_pos + 10], 16)
    request = Request(name, q_type, q_class)
    pos = (int(answer[start_pos + 10:start_pos + 14], 16) - 49152) * 2
    stop = False
    domains = []
    while not stop:
        pos, domains, i, domain, stop = find_domain_names(answer, pos, domains, 1, domain, stop)
    name = format_name(domains)
    t = answer[start_pos + 14:start_pos + 18]
    _type = int(answer[start_pos + 14:start_pos + 18], 16)
    _class = int(answer[start_pos + 18:start_pos + 22], 16)
    ttl = int(answer[start_pos + 26:start_pos + 30], 16)
    rd_length = int(answer[start_pos + 30:start_pos + 34], 16)
    rd_data = input_rd_data(answer[start_pos + 34:start_pos + 34 + rd_length * 2], rd_length)
    print(rd_data)


message = "aa bb 01 00 00 01 00 00 00 00 00 00 " \
          "07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00 01"

response = "aabb81800002000100000000076578616d706c6503636f6d00c0180000010001c00c00010001000006e600045db8d822"
# response = send_udp_message(message, "8.8.8.8", 53)
print(format_hex(response))
answer_parser(response)
c = cache.Cache(expire=10, starttime=time.time())
