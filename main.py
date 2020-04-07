import socket


def take_request():
    sock = socket.socket()
    sock.bind(('', 53))
    sock.listen(5)
    conn, addr = sock.accept()

    print('conn: ', addr)

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data)
    except ConnectionResetError:
        conn.close()
    finally:
        conn.close()


if __name__ == '__main__':
    take_request()
