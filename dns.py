import socket
import binascii


class DNSAnswer:
    def __init__(self, id, flags, request_count, answer_count,
                 add_count, binary_address, request_type, request_class, off_name,
                 answer_type, answer_class, ttl, ip_len, ip
                 ):
        self.id = id
        self.binary_address = binary_address
        self.flags = flags
        self.request_count = request_count
        self.answer_count = answer_count
        self.add_count = add_count
        self.request_type = request_type
        self.request_class = request_class
        self.off_name = off_name
        self.answer_type = answer_type
        self.answer_class = answer_class
        self.ttl = ttl
        self.ip_len = ip_len
        self.ip = ip


def form_dns_msg(domain_addr):
    id = bytearray("ab", "UTF-8")
    flags = bytes([1, 0])
    req_count = bytes([0, 1])
    answer_count = bytes([0, 0])
    add_count = bytes([0, 0, 0, 0])

    domains = domain_addr.split('.')
    binary_address = bytes([0])

    for domain in domains:
        length = bytes([len(domain)])
        address = length + bytearray(domain, "UTF-8")
        binary_address += address
    binary_address += bytes([0])
    request_type = bytes([0, 1])
    request_class = bytes([0, 1])
    return id + flags + req_count + answer_count + add_count + binary_address + request_type + request_class


def send_udp_packet(hex_number, dns_server_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(10)
        sock.sendto(hex_number, (dns_server_ip, port))
        answer, address = sock.recvfrom(1024)
    except socket.timeout:
        print("Время ожидания истекло")
        return None, None
    finally:
        sock.close()
    return answer, address


def parse_dns_answer(binary_data):
    data_hex = binascii.b2a_hex(binary_data)
    id = data_hex[0:2]
    flags = data_hex[2:4]
    request_count = data_hex[4:6]
    answer_count = data_hex[6:8]
    add_count = data_hex[8:12]

    len_name = 12
    while True:
        len_name += 1
        if data_hex[len_name] == 0:
            break
    binary_address = data_hex[12:len_name]
    tail = data_hex[len_name:]
    request_type = tail[0:2]
    request_class = tail[2:4]
    off_name = tail[4:6]
    answer_type = tail[6:8]
    answer_class = tail[8:10]
    ttl = tail[10:14]
    len_ip = tail[14:16]
    ip = tail[16:]
    ip = "".join([number + "." for number in ip])[:-1]
    return DNSAnswer(id, flags, request_count, answer_count, add_count, binary_address, request_type, request_class,
                     off_name,
                     answer_type, answer_class, ttl, len_ip, ip)


if __name__ == '__main__':
    hex = binascii.b2a_hex(form_dns_msg("example.com"))
    for i in range(0, len(hex), 2):
        print(bytes([hex[i]]), bytes([hex[i + 1]]), '\n')
    binary_data, ip_address = send_udp_packet(hex, '77.88.8.8', 53)
    answer = parse_dns_answer(binary_data)
    print(answer.ip)
