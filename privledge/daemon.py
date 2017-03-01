""" A daemon thread manager that receives input from the command line
"""

import threading
import json
import time
from privledge import utils
from privledge.ledger import Ledger
from socket import *
from privledge import settings


lock = threading.Lock()
ledger = None
_private_key = None
_udp_thread = None
_tcp_thread = None


# Create a ledger with a new public and private key
def create_ledger(new_public_key, new_private_key):
    global ledger, _private_key, _udp_thread, _tcp_thread
    ledger = Ledger(new_public_key)
    _private_key = new_private_key

    # Spawn UDP Discovery Listener thread
    _udp_thread = UDPListener(settings.BIND_IP, settings.BIND_PORT)
    _udp_thread.start()

    # Spawn TCP Listener thread
    _tcp_thread = TCPListener(settings.BIND_IP, settings.BIND_PORT)
    _tcp_thread.start()



# Join a ledger with a specified public key
def join_ledger(public_key_hash, members):
    global ledger

    # Check to make sure we aren't part of a ledger yet
    # if ledger is not None:
    #     print("You are already a member of a ledger")
    #     return

    join_thread = JoinLedgerThread(public_key_hash, members)
    join_thread.start()
    join_thread.join()

    # Parse through the worker threads' results
    results = join_thread.results
    for target in results:
        value = results[target]
        if value is not None and value is not '':
            decoded = json.loads(results[target])

            '''
            Look for a json encoded string in this format:
                status (200/404)
                public_key (public key)
            '''

            # If the message is properly formatted, try to parse the message as a key
            if 'status' in decoded and decoded['status'] == 200 and 'public_key' in decoded:
                key = utils.get_key(decoded['public_key'])
                if public_key_hash == utils.gen_id(key.publickey().exportKey()):
                    # Hooray! Create new ledger and add new member
                    if ledger is None:
                        ledger = Ledger(key.publickey())
                    ledger.add_peer(target[0])
                    continue

        utils.log_message("Not a valid response from {0}: {1}".format(target[0], results[target]))


def leave_ledger():
    global ledger, _udp_thread, _tcp_thread

    if ledger is not None:
        message = "Left ledger {0}".format(ledger.id)
        ledger = None

        # Kill udp listener thread
        _udp_thread.stop.set()
        _udp_thread.join()
        _udp_thread = None

        # Kill tcp listener thread

    else:
        message = "Not a member of a ledger, cannot leave"

    return message

def discover_ledger(ip, timeout = settings.DISCOVERY_TIMEOUT):
    # We need to start discovery process
    print("Searching for available ledgers for {0} seconds...".format(timeout))
    results = dict()

    # Set up discover thread
    found_event = threading.Event()
    discover_thread = DiscoverLedgerThread(found_event, results, timeout, ip)
    discover_thread.start()

    # Wait for discovery to finish
    for i in range(1, timeout):
        if found_event.is_set():
            print('*', end='', flush=True)
            found_event.clear()
        else:
            print('°', end='', flush=True)
        time.sleep(1)

    # Clean up thread
    discover_thread.join()

    # Return found ledgers
    return results


# Join a specified ledger
class JoinLedgerThread(threading.Thread):

    def __init__(self, root_hash, members):
        super(JoinLedgerThread, self).__init__()
        with lock:
            utils.log_message("Starting Ledger Join Thread: {0}".format(root_hash))
        self._root_hash = root_hash
        self._members = members
        self.results = dict()

    def run(self):

        threads = dict()

        # Spawn a TCP message thread for each member of the ledger
        for member in self._members:
            with lock:
                utils.log_message("Spawning TCP Connection Thread to {0}:{1}".format(member[0], member[1]))
            join_message = {'request': 'join', 'message': self._root_hash.decode()}
            join_message = json.dumps(join_message)
            thread = TCPMessageThread(member, join_message)
            thread.start()
            threads[member] = thread

        # Wait for all the threads to finish
        for address in threads:
            threads[address].join()
            self.results[address] = threads[address].message



# Generic TCP Message Passing Class
class TCPMessageThread(threading.Thread):

    def __init__(self, target, message, timeout=5):
        super(TCPMessageThread, self).__init__()
        with lock:
            utils.log_message("Sending Message to {0} {1}: {2}{3}".format(target[0], target[1], message[:10], '...'))
        self._target = target
        self.message = message
        self._timeout = timeout

    def run(self):
        tcp_message_socket = socket(AF_INET, SOCK_STREAM)

        try:
            tcp_message_socket.connect(self._target)
            tcp_message_socket.sendall(self.message.encode())

            # Store data in buffer until other side closes connection
            self.message = ''
            data = True

            while data:
                data = tcp_message_socket.recv(4096)
                self.message += data.decode()

            with lock:
                utils.log_message(
                    "Received Response from {0} {1}: {2}{3}".format(self._target[0], self._target[1], self.message[:10],
                                                                    '...'))

        except Exception as e:
            print("Could not connect to the specified ledger")
        finally:
            tcp_message_socket.close()




# Thread for discovering Ledgers
class DiscoverLedgerThread(threading.Thread):

    def __init__(self, found_event, results, timeout=10, ip='<broadcast>', port=2525):
        super(DiscoverLedgerThread, self).__init__()
        with lock:
            utils.log_message("Starting Ledger Discovery Thread")
        self._found_event = found_event
        self._results = results
        self._timeout = timeout
        self._ip = ip
        self._port = port

    def run(self):
        # Send out discovery query
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto(''.encode(), (self._ip, self._port))
        try:
            # Listen for responses for 10 seconds
            s.settimeout(self._timeout)
            while True:
                data, address = s.recvfrom(1024)

                with lock:
                    utils.log_message("Discovered ledger {0} at {1}".format(data, address))

                # Received response
                # Is the hash already in our list?
                if data not in self._results:
                    # If hash isn't in the list, create a new set and add address to it
                    self._results[data] = set()
                # Since there's already a set for our hash, we add to it
                self._results[data].add(address)

                self._found_event.set()
        except Exception as e:
            utils.log_message("Exception: {0}".format(e))
        finally:
            s.close()


class UDPListener(threading.Thread):

    def __init__(self, ip, port):
        super(UDPListener, self).__init__()
        with lock:
            utils.log_message("Starting UDP Listener Thread")
        self.daemon = True
        self._port = port
        self._ip = ip
        self.stop = threading.Event()

    def run(self):
        # Listen for ledger client connection requests
        with lock:
            utils.log_message("Listening for ledger discovery queries on port {0}".format(self._port))

        discovery_listener = socket(AF_INET, SOCK_DGRAM)
        discovery_listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        discovery_listener.bind((self._ip, self._port))
        discovery_listener.setblocking(False)

        # Non-blocking socket loop that can be interrupted with a signal/event
        while True and not self.stop.is_set():
            try:
                data, addr = discovery_listener.recvfrom(1024)
            except Exception as e:
                continue
            else:
                utils.log_message("Received discovery inquiry from {0}, responding...".format(addr))
                discovery_listener.sendto(ledger.id.encode(), addr)

        discovery_listener.close()


class TCPListener(threading.Thread):

    def __init__(self, ip = settings.BIND_IP, port = settings.BIND_PORT):
        super(TCPListener, self).__init__()
        with lock:
            utils.log_message("Starting TCP Listener Thread")
        self.daemon = True
        self._port = port
        self._ip = ip
        self.stop = threading.Event()
        self.stop.clear()

        self.tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.tcp_server_socket.setblocking(False)
        self.tcp_server_socket.bind((self._ip, self._port))

    def run(self):
        # Listen for ledger client connection requests
        with lock:
            utils.log_message("Listening for ledger messages on port {0}".format(self._port))

        try:
            self.tcp_server_socket.listen(5)

            # List for managing spawned threads
            socket_threads = []

            # Non-blocking socket loop that can be interrupted with a signal/event
            while True and not self.stop.is_set():
                try:
                    client_socket, address = self.tcp_server_socket.accept()

                    # Spawn thread
                    client_thread = TCPConnectionThread(client_socket)
                    client_thread.start()
                    socket_threads.append(client_thread)

                except Exception as e:
                    continue

            # Clean up all the threads
            for thread in socket_threads:
                thread.join()

        except Exception as e:
            print("Could not bind to port: {0}".format(e))
        finally:
            self.tcp_server_socket.close()




# Generic inbound TCP connection handler
class TCPConnectionThread(threading.Thread):

    def __init__(self, socket):
        super(TCPConnectionThread, self).__init__()
        with lock:
            utils.log_message("Spawning TCP Connection Thread from {0}".format(socket.getsockname()))
        self._socket = socket


    def run(self):
        global ledger

        # Get message
        message = ''
        message_size = None
        try:
            while True:
                if message_size is None:
                    data = self._socket.recv(4)
                    # Convert first 4 bytes to an integer
                    message_size = int(data.decode())
                elif len(message) < message_size:
                    data = self._socket.recv(4096)
                    message+=data.decode()
                else:
                    break
        except ValueError as e:
            utils.log_message('Received invalid packet from {0}'.format(self._socket.getsockname()))
            return
        finally:
            self._socket.close()


        with lock:
            utils.log_message("Received message from {0}:\n{1}".format(self._socket.getsockname(), message))

        decoded = json.loads(message)

        '''
        Look for a json encoded string in this format:
            request (join/add/etc)
            message (key/hash/etc)
        '''

        response = dict()

        # Process different requests
        if 'request' in decoded:

            # Join request
            if decoded['request'] == 'join':

                # Does the hash match ours?
                if 'message' in decoded and decoded['message'] == ledger.id:

                    response['status'] = 200
                    response['public_key'] = ledger.pubkey.exportKey().decode()

        # No response, send error status
        else:
            response['status'] = 404

        # Send response & close socket
        response_json = json.dumps(response)
        with lock:
            utils.log_message("Responded with message to {0}:\n{1}".format(self._socket.getsockname(),response_json))
        self._socket.sendall(len(response_json)+response_json.encode())
        self._socket.shutdown()
        self._socket.recv()
        self._socket.close()