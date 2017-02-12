from cmd import Cmd
from sshpubkeys import SSHkey
from socket import *

import time

class PrivledgeShell(Cmd):

    def do_init(self, args):
        """Initialize the ledger with a provided Root of Trust (RSA Public Key)"""
        if len(args) == 0:
            print("Please provide a public key as your new Root of Trust")
        elif isPubKey(args[0]):
             print("to be added")

    def do_quit(self):
        """Quits the shell"""
        print("Quitting")
        raise SystemExit

    def do_list(self, args):
        """Attempts to find existing ledgers"""
        if len(args) == 0:
            # search LAN for available ledgers
            print("Looking for available ledgers for 30 seconds...")
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            s.sendto('Hey you guys!', ('<broadcast>', 2525))

            results = dict()
            timeout = time.time() + 30
            while time.time() < timeout:
                data,address = s.recvfrom(1024)
                results[address] = data
                time.sleep(1)

            print(results)


if __name__ == '__main__':
    prompt = PrivledgeShell()
    prompt.prompt = '> '
    prompt.cmdloop('Welcome to Privledge Shell...')


def emptyline(self):
    pass

def isPubKey(args):
    return True