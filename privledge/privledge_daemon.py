import socket
import threading
from privledge import utilities

BIND_IP = ''
BIND_PORT = 2525

lock = threading.Lock()


class PrivledgeDaemon(threading.Thread):
    """ A Daemon thread that receives input from the command line
    """

    def __init__(self):
        super(PrivledgeDaemon, self).__init__()
        with lock:
            utilities.log_message("Starting Privledge Daemon")
        self.daemon = True

    def run(self):
        # Spawn UDP Listener thread
        udp_thread = UDPListener(BIND_IP, BIND_PORT)
        udp_thread.start()

        # Spawn TCP Listener thread
        tcp_thread = TCPListener(BIND_IP, BIND_PORT)
        tcp_thread.daemon = True
        tcp_thread.start()


class UDPListener(threading.Thread):

    def __init__(self, ip, port):
        super(UDPListener, self).__init__()
        with lock:
            utilities.log_message("Starting UDP Listener Thread")
        self.daemon = True
        self.port = port
        self.ip = ip

    def run(self):
        # Listen for ledger client connection requests
        with lock:
            utilities.log_message("Listening for ledger discovery queries on port " + str(self.port))

        discovery_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        discovery_listener.bind((self.ip, self.port))

        while True:
            data, addr = discovery_listener.recvfrom(1024)
            print(data.decode())

            # Reply if we did not initiate the discovery process
            if addr != discovery_listener.getsockname()[0]:
                print(addr)
                # if data=="Hey you guys!":
                discovery_listener.sendto("Sup Homie!".encode(), addr)


class TCPListener(threading.Thread):

    def __init__(self, ip, port):
        super(TCPListener, self).__init__()
        with lock:
            utilities.log_message("Starting TCP Listener Thread")
        self.daemon = True
        self.port = port
        self.ip = ip

    def run(self):
        # Listen for ledger client connection requests
        # with lock:
        #     utilities.log_message("Listening for ledger discovery queries on port " + str(self.port))
        #
        # server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # server.setblocking(False)
        # server.bind((BIND_IP, self.port))
        #
        # while True:
        #     data, addr = server.recvfrom(1024)
        #     print(data.decode())
        #     print(addr)
        #     # if data=="Hey you guys!":
        #     server.sendto("Sup Homie!".encode(), addr)
        pass
