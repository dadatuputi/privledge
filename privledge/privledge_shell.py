from cmd import Cmd
from sshpubkeys import SSHKey
from socket import *
import time

from privledge.privledge_daemon import PrivledgeDaemon
from privledge.utilities import *


class PrivledgeShell(Cmd):

    def __init__(self, daemon):
        super(PrivledgeShell, self).__init__()
        self.prompt = '> '
        self.cmdloop('Welcome to Privledge Shell...')

    def do_init(self, args):
        """Initialize the ledger with a provided Root of Trust (RSA Public Key)"""
        if len(args) == 0:
            print("Please provide a public key as your new Root of Trust")
        else:
            if (args.lower() == "default"):
                key = open('id_rsa_test.pub')
                args=key.read()
                key.close()
                print("Importing Test Key...")
                log_message("DO NOT USE IN PRODUCTION:", Level.HIGH)
                print(args)

            ssh = SSHKey(args.strip(), strict_mode=True)

            try:
                ssh.parse()
                print("\nKey Info:")
                print("\tBits: " + str(ssh.bits))
                print("\tHash: " + ssh.hash_sha256())
                print("\tComment: " + ssh.comment)
            except Exception as err:
                print("Invalid key: "+ str(err))

    def do_debug(self, args):
        """Toggles printing of debug information"""
        global debug

        if len(args) == 0:
            debug = not debug
        elif args.lower() in ['true', 'on', '1']:
            debug = True
        elif args.lower() in ['false', 'off', '0']:
            debug = False

        print("Debug mode is {}".format(debug))


    def do_quit(self, args):
        """Quits the shell"""
        print("Quitting")
        raise SystemExit

    def do_list(self, args):
        """Attempts to find existing ledgers"""
        ip = '<broadcast>'
        if len(args) > 0:
            # search LAN for available ledgers
            ip = args[0]

        print("Searching for available ledgers for 10 seconds...")
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.sendto('Hey you guys!'.encode(), (ip, 2525))
        try:
            # Listen for responses for 10 seconds
            s.settimeout(10)
            results = dict()
            while True:
                data,address = s.recvfrom(1024)
                print("Response from " + str(address) + ": " + data.decode())
                results[address] = data
                time.sleep(1)
        except Exception as e:
            pass

        if len(results) > 0:
            print("Found " + str(len(results)) + " available ledgers")
        else:
            print("No ledgers found.")

def emptyline(self):
    pass