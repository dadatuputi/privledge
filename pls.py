from cmd import Cmd
from sshpubkeys import SSHKey
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
        ip = '<broadcast>'
        if len(args) > 0:
            # search LAN for available ledgers
            ip = args[0]

        print("Looking for available ledgers for 10 seconds...")
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto('Hey you guys!'.encode(), (ip, 2525))
        try:
            s.settimeout(10)

            results = dict()
            timeout = time.time() + 10
            while time.time() < timeout:
                data,address = s.recvfrom(1024)
                results[address] = data
                time.sleep(1)
            print("Time's up!")
            print(results)
        except Exception as e:
            pass

        if len(results) > 0:
            print(results)
        else:
            print("No ledgers found.")



if __name__ == '__main__':
    prompt = PrivledgeShell()
    prompt.prompt = '> '
    prompt.cmdloop('Welcome to Privledge Shell...')


def emptyline(self):
    pass

def isPubKey(args):
    return True