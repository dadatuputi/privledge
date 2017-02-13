import socket

BIND_IP = '0.0.0.0'
BIND_PORT = 2525

def udp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(( BIND_IP, BIND_PORT))
    print("Waiting on port: " + str(BIND_PORT))

    while 1:
        data, addr = server.recvfrom(1024)
        print(data)
        print(addr)
        #if data=="Hey you guys!":
        server.sendto("Sup Homie!".encode(), addr)

if __name__ == '__main__':
    udp_server()