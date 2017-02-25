from cmd import Cmd
from sshpubkeys import SSHKey

from privledge import utils
from privledge import settings
from privledge.privledge_daemon import DiscoverLedgerThread

import time
import threading
import socket
from os import system


class PrivledgeShell(Cmd):

    results = dict()

    def __init__(self, daemon):
        super(PrivledgeShell, self).__init__()

        self.daemon = daemon

        # Start the command loop - these need to be the last lines in the initializer
        self.prompt = '> '
        self.cmdloop('Welcome to Privledge Shell...')

    def do_init(self, args):
        """Initialize the ledger with a provided Root of Trust (RSA Public Key)"""

        # Give error with no key, use default key, or provide
        if len(args) == 0:
            print("Please provide an RSA key as your new Root of Trust.")
            return
        else:
            args_list = args.split()
            if args_list[0].lower() == "generate":
                # Generate an RSA key

                if len(args_list) == 1:
                    # Generate a RSA key in memory
                    key = utils.generate_openssh_key()
                else:
                    # Generate and save RSA key
                    key = utils.generate_openssh_key(True, args_list[0])

            else:
                # Try to import provided key
                key = utils.get_key(args)

                if key is None:
                    print("Could not import the provided key")
                    return

        # If we made it this far we have a valid key
        # Store generated key in our daemon for now
        try:
            key_contents = key.publickey().exportKey('OpenSSH').decode()
            ssh = SSHKey(key_contents, strict_mode=True)
            ssh.parse()
            key.pub = ssh
            self.daemon.set_root(key)

            print("\nPublic Key Info:")
            print("\tBits: {0}".format(len(key.publickey().exportKey('OpenSSH'))*8))
            print("\tHash: {0}".format(ssh.hash_sha256()))
            utils.log_message("Added key as a new Root of Trust", utils.Level.MEDIUM, True)
        except Exception as err:
            print("Invalid key: "+ str(err))


    def do_debug(self, args):
        """Toggles printing of debug information"""

        if len(args) == 0:
            settings.debug = not settings.debug
        elif args.lower() in ['true', 'on', '1']:
            settings.debug = True
        elif args.lower() in ['false', 'off', '0']:
            settings.debug = False

        print("Debug mode is {}".format(settings.debug))


    def do_quit(self, args):
        """Quits the shell"""
        print("Quitting")
        raise SystemExit

    def do_list(self, args):
        """Attempt to find existing ledgers. Provide an ip address, otherwise the local broadcast will be used. You may force an update by entering 'update'"""

        # No args provided
        if len(args) == 0:
            if len(self.results) > 0:
                # Look for cached ledger list
                self.display_ledger()
                return
            else:
                # Force update if no previous results
                args = 'update'

        ip = '<broadcast>'

        # Check for 'update' keyword
        if len(args) > 0:
            if args.lower().strip() != 'update':
                ip = args

                # Check for a valid IP
                try:
                    socket.inet_aton(ip)
                except socket.error:
                    print("You entered an invalid IP address")
                    return

            # We need to start discovery process
            print("Searching for available ledgers for {0} seconds...".format(settings.DISCOVERY_TIMEOUT))
            self.results.clear()

            # Set up discover thread
            found_event = threading.Event()
            discover_thread = DiscoverLedgerThread(found_event, self.results, settings.DISCOVERY_TIMEOUT, ip)
            discover_thread.start()

            # Wait for discovery to finish
            for i in range(1, settings.DISCOVERY_TIMEOUT):
                if found_event.is_set():
                    print('*', end='', flush=True)
                    found_event.clear()
                else:
                    print('°', end='', flush=True)
                time.sleep(1)

            discover_thread.join()

            # Process results
            self.display_ledger()

    def default(self, args):
        """Passes unrecognized commands through to the operating system"""

        system(args)



    def display_ledger(self):
        print("\nFound {0} available ledgers".format(str(len(self.results))))

        if len(self.results) > 0:

            i = 0
            for ledger in self.results:
                i += 1
                print("{0}: ({1} members) {2}".format(i, len(self.results[ledger]), ledger.decode()))


def emptyline(self):
    pass