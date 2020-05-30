from record import *

cache = {}


def format_name(domains):
    results = []
    for d in domains:
        res = []
        for domain in d:
            pairs = [int(domain[i:i + 2], 16) for i in range(0, len(domain), 2)]
            res.append("".join([chr(i) for i in pairs]))
        results.append(".".join(res))
    return results


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
        pos = (int(answer[start_pos:start_pos + 4], 16) - 49152) * 2
        while pos < start_pos - 2:
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


def get_name(answer, start_pos, domains):
    domain = []
    stop = False
    while not stop:
        start_pos, domains, i, domain, stop = find_domain_names(answer, start_pos, domains, 1, domain, stop)
    return format_name(domains)


def parse_answer(answer):
    questions = int(answer[8:12], 16)  # число запросов
    answer_rrs = int(answer[12:16], 16)
    authority_rrs = int(answer[16:20], 16)
    additional_rrs = int(answer[20:24], 16)
    start_pos = 24
    domains = []
    i = questions
    domain = []
    while i > 0:
        start_pos, domains, i, domain, _ = find_domain_names(answer, start_pos, domains, i, domain, True)
    stop = False
    domains = []
    j = answer_rrs
    start_pos += 14

    answers = []
    while j > 0:
        pos = (int(answer[start_pos - 4:start_pos], 16) - 49152) * 2
        while not stop:
            pos, domains, i, domain, stop = find_domain_names(answer, pos, domains, 1, domain, stop)
        name = format_name(domains)[0]
        _type = int(answer[start_pos:start_pos + 4], 16)
        ttl = int(answer[start_pos + 12:start_pos + 16], 16)
        rd_length = int(answer[start_pos + 16:start_pos + 20], 16) * 2
        data = answer[start_pos + 16:start_pos + 20 + rd_length]
        answ = Record(_type, ttl, data)
        if cache.get((name, _type), None) is None:
            cache[(name, _type)] = [answ]
        else:
            cache[(name, _type)].append(answ)
        answers.append(Record(_type, ttl, data))
        start_pos += 24 + rd_length
        j -= 1
    j = authority_rrs
    stop = False
    domains = []
    # auth servers
    while j > 0:
        pos = (int(answer[start_pos - 4:start_pos], 16) - 49152) * 2
        while not stop:
            pos, domains, i, domain, stop = find_domain_names(answer, pos, domains, 1, domain, stop)

        name = format_name(domains)[0]
        _type = int(answer[start_pos:start_pos + 4], 16)
        ttl = int(answer[start_pos + 12:start_pos + 16], 16)
        data_length = int(answer[start_pos + 16:start_pos + 20], 16) * 2
        data = answer[start_pos + 16:start_pos + 20 + data_length]
        ans = Record(_type, ttl, data)
        if cache.get((name, _type), None) is None:
            cache[(name, _type)] = [ans]
        else:
            cache[(name, _type)].append(ans)
        j -= 1

        start_pos += 24 + data_length
    j = additional_rrs
    # additional records
    while j > 0:
        result, start_pos = find_mailbox_or_name_server(answer, start_pos - 4)
        name = format_name([result[0]])[0]
        _type = int(answer[start_pos:start_pos + 4], 16)
        ttl = int(answer[start_pos + 8:start_pos + 16], 16)
        data_length = int(answer[start_pos + 16:start_pos + 20], 16) * 2
        data = answer[start_pos + 16:start_pos + 20 + data_length]
        ar = Record(_type, ttl, data)
        if cache.get((name, _type), None) is None:
            cache[(name, _type)] = [ar]
        else:
            cache[(name, _type)].append(ar)
        start_pos += 24 + data_length
        j -= 1
    print(1)


def find_mailbox_or_name_server(answer, start_pos):
    result = []
    domain = []
    domains = []
    stop = False
    while True:
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
            pos = (int(answer[start_pos:start_pos + 4], 16) - 49152) * 2
            while answer[pos:pos + 2] != "00" and not stop:
                pos, domains, _, domain, stop = find_domain_names(answer, pos, domains, 1, domain, stop)
            for d in domains:
                result.append(d)
            start_pos += 4
            break
    return result, start_pos
