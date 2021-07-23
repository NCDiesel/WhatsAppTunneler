import socket

HOST = ''
PORT = 44455
BUFFER_SIZE = 1024

def start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        
        while True:
            conn, addr = s.accept()
            print('Connection from ', addr)
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            tunnel_request(data, conn)

def tunnel_request(data, conn):
    # CODE TO AUTOMATE MANUAL WRITING OF WHATSAPP MESSAGE
    # SENDS TO SERVER
    # GETS RESPONSE
    write(data)
    r = read()
    message = r + (BUFFER_SIZE - len(r)) * ' '
    conn.send(message.encode())

def write(data):
    data = data.decode().split('\n')
    request = data[0]
    print("Forwarding request: " + request)
    pass

def read():
    print("Success!")
    return "testing\n"

def pp(data):
    print(data.decode())

start()