import threading
from privledge import utils
from socket import *

BIND_IP = ''
BIND_PORT = 2525

lock = threading.Lock()


class PrivledgeDaemon():
    """ A Daemon thread that receives input from the command line
    """
    global root
    root = None

    def __init__(self):
        utils.log_message("Starting Privledge Daemon")

        # Spawn TCP Listener thread
        self.tcp_thread = TCPListener(BIND_IP, BIND_PORT)
        self.tcp_thread.daemon = True
        self.tcp_thread.start()

    def set_root(self, new_root):
        global root
        root = new_root

        # Spawn UDP Discovery Listener thread
        if not hasattr(self, 'udp_thread'):
            self.udp_thread = UDPListener(BIND_IP, BIND_PORT)
            self.udp_thread.start()




class DiscoverLedgerThread(threading.Thread):

    def __init__(self, found_event, results, timeout=10, ip='<broadcast>', port=2525):
        super(DiscoverLedgerThread, self).__init__()
        with lock:
            utils.log_message("Starting Ledger Discovery Thread")
        self.found_event = found_event
        self.results = results
        self.timeout = timeout
        self.ip = ip
        self.port = port

    def run(self):
        # Send out discovery query
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto(''.encode(), (self.ip, self.port))
        try:
            # Listen for responses for 10 seconds
            s.settimeout(self.timeout)
            while True:
                data, address = s.recvfrom(1024)

                # Received response
                # Is the hash already in our list?
                if data not in self.results:
                    # If hash isn't in the list, create a new set and add address to it
                    self.results[data] = set()
                # Since there's already a set for our hash, we add to it
                self.results[data].add(address)

                self.found_event.set()
        except Exception as e:
            s.close()

        return self.results


class UDPListener(threading.Thread):

    def __init__(self, ip, port):
        super(UDPListener, self).__init__()
        with lock:
            utils.log_message("Starting UDP Listener Thread")
        self.daemon = True
        self.port = port
        self.ip = ip

    def run(self):
        # Listen for ledger client connection requests
        with lock:
            utils.log_message("Listening for ledger discovery queries on port " + str(self.port))

        discovery_listener = socket(AF_INET, SOCK_DGRAM)
        discovery_listener.bind((self.ip, self.port))

        while True:
            data, addr = discovery_listener.recvfrom(1024)
            utils.log_message("Received discovery inquiry from {0}, responding...".format(addr))
            discovery_listener.sendto(root.pub.hash_sha256().encode(), addr)


class TCPListener(threading.Thread):

    def __init__(self, ip, port):
        super(TCPListener, self).__init__()
        with lock:
            utils.log_message("Starting TCP Listener Thread")
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
