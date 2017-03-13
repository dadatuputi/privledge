""" A daemon thread manager that receives input from the command line
"""

import time
from privledge.ledger import Ledger
from privledge import block
from privledge.messaging import *


ledger = None
peers = dict()
_privkey = None
_udp_thread = None
_udp_hb_thread = None
_tcp_thread = None


# Create a ledger with a new public and private key
def create_ledger(pubkey, privkey):
    global ledger, _privkey

    # Create root block
    pubkey_hash = utils.gen_hash(pubkey)
    root_block = block.Block(block.BlockType.root, None, pubkey, pubkey_hash)
    root_block.sign(privkey, pubkey_hash)

    ledger = Ledger(root_block)
    _privkey = privkey

    # Start Listeners
    ledger_listeners(True)


def ledger_listeners(start):
    global _udp_thread, _udp_hb_thread, _tcp_thread

    if start:
        # Spawn UDP Persistent Listener thread
        _udp_thread = UDPListener(settings.BIND_IP, settings.BIND_PORT)
        _udp_thread.start()

        # Spawn UDP Heartbeat thread
        _udp_hb_thread = UDPHeartbeat()
        _udp_hb_thread.start()

        # Spawn TCP Listener thread
        _tcp_thread = TCPListener(settings.BIND_IP, settings.BIND_PORT)
        _tcp_thread.start()

    else:
        # Kill udp listener thread
        _udp_thread.stop.set()
        _udp_thread.join()
        _udp_thread = None

        # Kill udp hb thread
        _udp_hb_thread.stop.set()
        _udp_hb_thread.join()
        _udp_hb_thread = None


        # Kill tcp listener thread
        _tcp_thread.stop.set()
        _tcp_thread.join()
        _tcp_thread = None


# Join a ledger with a specified public key
def join_ledger(public_key_hash, member):
    global ledger

    # Check to make sure we aren't part of a ledger yet
    if ledger is not None:
        print("You are already a member of a ledger")
        return

    utils.log_message("Spawning TCP Connection Thread to {0}:{1}".format(member[0], member[1]))
    join_message = Message('join', public_key_hash)
    thread = TCPMessageThread(member, join_message)
    thread.start()
    thread.join()

    # Parse through the worker threads' results
    results = thread.message
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
                key_hash = utils.gen_hash(key.publickey().exportKey())
                if public_key_hash == key_hash:
                    # Hooray! Create new ledger and add new member
                    if ledger is None:
                        ledger = Ledger(key.publickey())
                        utils.log_message("Joined ledger {0}".format(public_key_hash))

                        # Start Listeners
                        ledger_listeners(True)
                    ledger.add_peer(target[0])
                    continue

        utils.log_message("Not a valid response from {0}: {1}".format(target[0], results[target]))


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

def discover_ledgers(ip='<broadcast>', port=settings.BIND_PORT, timeout = settings.DISCOVERY_TIMEOUT):
    print("Searching for available ledgers for {0} seconds...".format(timeout))
    utils.log_message("Starting Ledger Discovery")

    results = dict()

    # Send out discovery query
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    message = Message(settings.MSG_TYPE_DISCOVER).prep_send()
    s.sendto(message.encode(), (ip, port))
    try:
        # Listen for responses for 10 seconds
        s.settimeout(timeout)
        while True:
            data, address = s.recvfrom(1024)

            try:
                message = json.loads(data.decode(), object_hook=message_decoder)

                if message.type == settings.MSG_TYPE_DISCOVER:
                    utils.log_message("Discovered ledger {0} at {1}".format(hash, address))

                    # Received response
                    # Is the hash already in our list?
                    if message.message not in results:
                        # If hash isn't in the list, create a new set and add address to it
                        results[message.message] = set()
                    # Since there's already a set for our hash, we add to it
                    results[message.message].add(address)

            except:
                utils.log_message("Malformed response from {0}: {1}".format(data, address))

    except OSError as e:
        utils.log_message("Exception: {0}".format(e))
    finally:
        s.close()

    return results