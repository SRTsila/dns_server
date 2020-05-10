class AuthoritativeNameServer:
    def __init__(self, name, _type, _class, ttl, data_length, name_server, mailbox, serial_number, refresh_interval,
                 retry_interval, expire_interval, minimum_ttl):
        self.name = name
        self._type = _type
        self._class = _class
        self.ttl = ttl
        self.data_length = data_length
        self.name_server = name_server
        self.mailbox = mailbox
        self.serial_number = serial_number
        self.refresh_interval = refresh_interval
        self.retry_interval = retry_interval
        self.expire_interval = expire_interval
        self.minimum_ttl = ttl


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
