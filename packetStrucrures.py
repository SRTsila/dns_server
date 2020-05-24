from time import time
from zz.utils import decimal_to_hex


class AuthoritativeNameServer:
    def __init__(self, name, _type, ttl, data, server_name):
        self.name = name
        self._type = _type
        self.ttl = round(time()) + ttl
        self.data = data
        self.server_name = server_name

    def can_live(self):
        return self.ttl > round(time())


class AdditionalRecords:
    def __init__(self, name, _type, ttl, data):
        self.name = name
        self._type = _type
        self.ttl = round(time()) + ttl
        self.data = data

    def can_live(self):
        return self.ttl > round(time())


class DNSPacket:
    def __init__(self, header, query, answers=None, authority_rrs=None, additional_rrs=None):
        self.answers = answers
        self.header = header
        self.query = query
        self.authority_rrs = authority_rrs
        self.additional_rrs = additional_rrs

    def __str__(self):
        return self.header.__str__() + self.query


class Answer:
    def __init__(self, name, _type, ttl, data):
        self.name = name
        self._type = _type
        self.ttl = round(time()) + ttl
        self.data = data

    def __getstate__(self) -> dict:
        state = {}
        state["name"] = self.name
        state["_type"] = self.name
        state["ttl"] = self.ttl
        state["data"] = self.data

    def can_live(self):
        return self.ttl > round(time())


class CacheInfo:
    def __init__(self, answers, authoritive_servers, additional_records):
        self.answers = answers
        self.authoritive_servers = authoritive_servers
        self.additional_records = additional_records
        # self.items = self.get_items_count()

    # def get_items_count(self):
    #     items = 0
    #     for _ in self.answers:
    #         items += 1
    #     for _ in self.authoritive_servers:
    #         items += 1
    #     for _ in self.additional_records:
    #         items += 1
    #     return items

    def check_ttl(self):
        for answer in self.answers:
            if answer.ttl < round(time()):
                self.answers.remove(answer)
        for server in self.authoritive_servers:
            if server.ttl < round(time()):
                self.authoritive_servers.remove(server)
        for record in self.additional_records:
            if record.ttl < round(time()):
                self.additional_records.remove(record)


class NewStrc:
    def __init__(self, _type, ttl, data):
        self.name = "c00c"
        self._type = _type
        self.ttl = ttl
        self.data = data
        self._class = "0001"

    def __str__(self):
        self.name + self._type + self._class + decimal_to_hex(self.ttl - time()).rjust(8, '0') + self.data

    def can_live(self):
        return self.ttl > time()


# class Flags:
#     def __init__(self, qr, aa, recursion_desired, recursion_available, error_code):
#         self.qr = qr
#         self.aa = aa
#         self.recursion_desired = recursion_desired
#         self.recursion_available = recursion_available
#         self.reply_code = error_code


# class Header:
#     def __init__(self, id, f, request_number, answer_count, ns_count, ar_count):
#         self.id = id
#         self.flags = flags
#         self.request_number = request_number
#         self.answer_count = answer_count
#         self.ns_count = ns_count
#         self.ar_count = ar_count

a = {1: 1}
print(a.get(2, None))
