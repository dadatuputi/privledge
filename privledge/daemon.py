""" A daemon thread manager that can be controlled from the privledge shell
"""

from privledge import block
from privledge import settings
from privledge import utils
from privledge import messaging
from privledge.ledger import Ledger

import json
import socket

ledger = None
peers = dict()
disc_ledgers = dict()
disc_peers = set()
_privkey = None
_udp_thread = None
_udp_hb_thread = None
_tcp_thread = None


def is_root():
    if ledger is not None and ledger.root is not None and _privkey is not None:
        return ledger.root.message == _privkey.publickey().exportKey().decode()
    else:
        return False


# Create a ledger with a new public and private key
def create_ledger(privkey):
    global ledger, _privkey

    # Generate public key and hash from the private key
    pubkey = privkey.publickey()

    # Create root block
    root_block = block.Block(block.BlockType.add_key, None, pubkey.exportKey().decode())
    root_block.sign(privkey)

    ledger = Ledger()
    ledger.append(root_block)
    _privkey = privkey

    # Start Listeners
    ledger_listeners(True)


def ledger_listeners(start):
    global _udp_thread, _udp_hb_thread, _tcp_thread

    if start:
        # Spawn UDP Persistent Listener thread
        _udp_thread = messaging.UDPListener(settings.BIND_IP, settings.BIND_PORT)
        _udp_thread.start()

        # Spawn TCP Listener thread
        _tcp_thread = messaging.TCPListener(settings.BIND_IP, settings.BIND_PORT)
        _tcp_thread.start()

        # Spawn UDP Heartbeat thread
        _udp_hb_thread = messaging.UDPHeartbeat()
        _udp_hb_thread.start()

    else:
        # Kill udp listener thread
        utils.log_message("Killing UDP Listening Thread...")
        _udp_thread.stop.set()
        _udp_thread.join()
        _udp_thread = None

        # Kill tcp listener thread
        utils.log_message("Killing TCP Listening Thread...")
        _tcp_thread.stop.set()
        _tcp_thread.join()
        _tcp_thread = None

        # Kill udp hb thread
        utils.log_message("Killing Heartbeat Thread...")
        _udp_hb_thread.stop.set()
        _udp_hb_thread.join()
        _udp_hb_thread = None


# Join a ledger with a specified public key
def join_ledger(public_key_hash, member):
    global ledger

    # Check to make sure we aren't part of a ledger yet
    if ledger is not None:
        print("You are already a member of a ledger")
        return

    utils.log_message("Spawning TCP Connection Thread to {0}".format(member))
    join_message = messaging.Message(settings.MSG_TYPE_JOIN, public_key_hash).prep_tcp()
    thread = messaging.TCPMessageThread(member, join_message)
    thread.start()
    thread.join()

    # If the message is a success, import the key
    try:

        message = json.loads(thread.message, object_hook=utils.message_decoder)

        if message.msg_type == settings.MSG_TYPE_SUCCESS:
            key = utils.get_key(message.msg)
            key_hash = utils.gen_hash(key.publickey().exportKey())

            if public_key_hash == key_hash:
                # Hooray! We have a match
                utils.log_message("Joined ledger {}".format(public_key_hash), utils.Level.FORCE)

                # Sync Ledger
                messaging.ledger_sync(member)

                # Request peers
                messaging.peer_sync(member)

                # Start Listeners
                ledger_listeners(True)

            else:
                raise ValueError('Public key returned does not match requested hash: {0}'.format(key_hash))

        else:
            raise ValueError('Response was not as expected: {0}'.format(message.msg_type))

    except (ValueError, TypeError) as e:
        utils.log_message("Not a valid response from {0}: {1}".format(member, e))


def leave_ledger():
    global ledger, _udp_thread, _tcp_thread

    if ledger is not None:
        message = "Left ledger {0}".format(ledger.id)
        ledger = None

        # Kill the listners
        ledger_listeners(False)

    else:
        message = "Not a member of a ledger, cannot leave"

    return message


def discover(ip='<broadcast>', port=settings.BIND_PORT, timeout = settings.DISCOVERY_TIMEOUT):

    utils.log_message("Starting Discovery for {} seconds".format(timeout))

    results = dict()

    # Get our IP address - I don't like this hack:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect((ip, port))
    ip_self = s.getsockname()[0]
    s.close()

    # Send out discovery query
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = messaging.Message(settings.MSG_TYPE_DISCOVER).__repr__()
    s.sendto(message.encode(), (ip, port))


    try:
        # Listen for responses for 10 seconds
        s.settimeout(timeout)
        while True:
            data, address = s.recvfrom(4096)

            try:
                message = json.loads(data.decode(), object_hook=utils.message_decoder)

                if message.msg_type == settings.MSG_TYPE_SUCCESS:
                    utils.log_message("Discovered ledger {0} at {1}".format(message.msg, address), utils.Level.MEDIUM)

                    # Received response
                    # Is the response our own ledger?
                    if address[0] == ip_self:
                        continue
                    # Is the hash already in our list?
                    if message.msg not in results:
                        # If hash isn't in the list, create a new set and add address to it
                        results[message.msg] = set()
                    # Since there's already a set for our hash, we add to it
                    results[message.msg].add(address)

            except:
                utils.log_message("Malformed response from {0}: {1}".format(data, address))

    except OSError as e:
        utils.log_message("Exception: {0}".format(e))
    finally:
        s.close()

    return results
