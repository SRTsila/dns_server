import socket
import binascii


class Flags:
    def __init__(self, qr, aa, rd, ra, rcode):
        self.qr = qr
        self.aa = aa
        self.rd = rd
        self.ra = ra
        self.rcode = rcode


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
    res = []
    for domain in domains:
        pairs = [int(domain[i:i + 2], 16) for i in range(0, len(domain), 2)]
        res.append("".join([chr(i) for i in pairs]))
    return ".".join(res)


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


def answer_parser(answer):
    id = answer[:4]
    flags_data = answer[4:8]
    flags = parse_flags(flags_data)
    dq_count = int(answer[8:12], 16)  # число запросов
    an_count = int(answer[12:16], 16)
    ns_count = int(answer[16:20], 16)
    ar_count = int(answer[20:24], 16)
    start_pos = 24
    domains = []
    i = dq_count
    while i > 0:
        domain_len = int(answer[start_pos:start_pos + 2], 16)
        if 64 > domain_len > 0:
            domains.append(take_standart_mark(domain_len, answer, start_pos))
            j = start_pos + 2 + domain_len * 2
            if answer[j:j + 2] == "00":
                i -= 1
            start_pos = start_pos + 2 + domain_len * 2
            c = answer[start_pos:start_pos + 2]
        elif domain_len >= 64:
            v = answer[start_pos:start_pos + 4]
            start_pos = int(answer[start_pos:start_pos + 4], 16) - 49152
            domain_len = int(answer[start_pos:start_pos + 2], 16)
            domains.append(take_standart_mark(domain_len, answer,start_pos))
        else:
            start_pos += 2
    name = format_name(domains)
    print(name)


message = "aa bb 01 00 00 01 00 00 00 00 00 00 " \
          "07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00 01"

response = "aabb81800002000100000000076578616d706c6503636f6d00c0180000010001c00c00010001000006e600045db8d822"
# response = send_udp_message(message, "8.8.8.8", 53)
print(format_hex(response))
answer_parser(response)
