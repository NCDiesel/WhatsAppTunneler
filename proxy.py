import socket

HOST = ''
PORT = 44455

def start():
    buffer_size = 1248

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)

        while 1:
            conn, addr = s.accept()
            print('Connection from ', addr)
            data = conn.recv(buffer_size)
            if data:
                print(data.decode())

start()