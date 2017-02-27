from cmd import Cmd
from privledge import utils
from privledge import settings
from privledge import daemon

import socket
from os import system


class PrivledgeShell(Cmd):

    results = dict()



    def __init__(self):
        super(PrivledgeShell, self).__init__()

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
            daemon.create_ledger(key.publickey(), key)
            hash = daemon.ledger.id

            print("\nPublic Key Hash: {0}".format(hash))
            utils.log_message("Added key ({0}) as a new Root of Trust".format(hash), utils.Level.MEDIUM, True)
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
        if args.lower().strip() != 'update':
            ip = args

            # Check for a valid IP
            try:
                socket.inet_aton(ip)
            except socket.error:
                print("You entered an invalid IP address")
                return

        self.results = daemon.discover_ledger(ip)

        # Process results
        self.display_ledger()



    def do_join(self, args):
        """Join a ledger previously identified by the list command"""

        # Check for no arguments
        if len(args) == 0:
            print("You must provide a ledger number")
            return

        # Check for a valid argument (is integer)
        number = 0
        try:
            number = int(args)

            # Check for valid argument (is valid ledger)
            if number < 0 or number > len(self.results):
                raise ValueError("Out of Bounds Error")
        except ValueError as e:
            print("{0}\nYou did not provide a valid number: '{1}'".format(e, args))
            return

        # Pass the daemon the hash and members
        daemon.join_ledger(list(self.results.keys())[number], list(self.results.values())[number])



    def do_leave(self, args):
        """Leave the currently joined ledger"""
        print(daemon.leave_ledger())



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