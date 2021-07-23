import socket

HOST = ''

def start():
    port = 44455
    buffer_size = 1024

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()

        
        while True:
            conn, addr = s.accept()
            print('Connection from ', addr)
            data = conn.recv(buffer_size)
            if not data:
                break

            pp(data)

            msg = "testing\n"
            msg_len = len(msg)
            message = (buffer_size - msg_len)*'' + msg
            conn.send(message.encode())

                
def pp(data):
    print(data.decode())


def tunnel_request(data, s):
    # CODE TO AUTOMATE MANUAL WRITING OF WHATSAPP MESSAGE
    # SENDS TO SERVER
    # GETS RESPONSE
    write()
    html = read()
    # print(html)
    s.send(html)

def write():
    pass

def read():
    return b'test'


start()