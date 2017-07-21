from cmd import Cmd
from privledge import utils
from privledge import settings
from privledge import daemon

import socket
import json
import os
from os import system


# Helper class for exit functionality
class ExitCmd(Cmd):
    @staticmethod
    def can_exit():
        return True

    def onecmd(self, line):
        r = super(ExitCmd, self).onecmd(line)
        if r and (self.can_exit() or input('exit anyway ? (yes/no):') == 'yes'):
            return True
        return False

    @staticmethod
    def do_exit(args):
        return True

    @staticmethod
    def help_exit():
        print("Exit the interpreter.")


# Helper class for shell command functionality
class ShellCmd(Cmd, object):
    @staticmethod
    def do_shell(s):
        os.system(s)

    @staticmethod
    def help_shell():
        print("Execute Shell Commands")


# Base Privledge Shell Class
class PrivledgeShell(ExitCmd, ShellCmd):

    results = dict()

    def __init__(self):
        super(PrivledgeShell, self).__init__()

        # Start the command loop - these need to be the last lines in the initializer
        self.update_prompt()
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
                    privkey = utils.privkey_generate()
                else:
                    # Generate and save RSA key
                    privkey = utils.privkey_generate(True, args_list[0])

            else:
                # Try to import provided key
                privkey = utils.get_key(args)

                if privkey is None:
                    print("Could not import the provided key")
                    return

        # If we made it this far we have a valid key
        # Store generated key in our daemon for now
        daemon.create_ledger(privkey)
        hash = daemon.ledger.id

        print("\nPublic Key Hash: {0}".format(hash))
        utils.log_message("Added key ({0}) as a new Root of Trust".format(hash), utils.Level.MEDIUM, True)

        self.update_prompt()

    def do_debug(self, args):
        """Toggles printing of debug information"""

        if len(args) == 0:
            settings.debug = not settings.debug
        elif args.lower() in ['true', 'on', '1']:
            settings.debug = True
        elif args.lower() in ['false', 'off', '0']:
            settings.debug = False

        print("Debug mode is {}".format(settings.debug))

        self.update_prompt()

    def do_quit(self, args):
        """Quits the shell"""

        print("Quitting")
        raise SystemExit

    def do_list(self, args):
        """Attempt to find existing ledgers. Provide an ip address, otherwise the local broadcast will be used.
        You may force an update by entering 'update'"""

        # No args provided
        if len(args) == 0:
            if len(self.results) > 0:
                # Look for cached ledger list
                utils.log_message("Using cached results; use 'list update' to force an update.", force=True)
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
                socket.inet_pton(socket.AF_INET, ip)
            except socket.error:
                print("You entered an invalid IP address")
                return

        self.results = daemon.discover_ledgers(ip)

        # Process results
        self.display_ledger()

    def do_join(self, args):
        """Join a ledger previously identified by the list command"""

        # Check for no arguments
        if len(args) == 0:
            print("You must provide a ledger number. Use the `list` command to show ledger numbers.")
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
        daemon.join_ledger(list(self.results.keys())[number-1], list(list(self.results.values())[number-1])[0])

    def do_leave(self, args):
        """Leave the currently joined ledger"""

        print(daemon.leave_ledger())

    def do_status(self, args):
        """Show current ledger status"""

        if daemon.ledger is not None:
            # Print ledger status
            print("You are a member of ledger {0} and connected to {1} peers.".format(daemon.ledger.id,
                                                                                len(daemon.peers)))
            # Detailed
            if args.lower() == 'detail':
                print("\nRoot of Trust:")
                print(daemon.ledger.root)
        else:
            # Print message if no ledger
            print("You are not a member of a ledger")

    def do_ledger(self, args):
        """Print the ledger"""

        ledger_list = daemon.ledger.to_list()

        # Print each block
        for block in ledger_list:
            print(block)

    def update_prompt(self):
        """Update the prompt based on system variables"""

        indicators = []

        if daemon.is_root():
            indicators.append('root')
        if settings.debug:
            indicators.append('debug')

        self.prompt = '|'.join(indicators) + '> '

    def display_ledger(self):
        print("Found {0} available ledgers".format(str(len(self.results))))

        if len(self.results) > 0:

            member = ''
            i = 0
            for ledger in self.results:
                i += 1
                if daemon.ledger is not None and daemon.ledger.id == ledger.strip():
                    member = '(member)'
                else:
                    member = ''
                print("{0} | {4}: ({1} members) {2} {3}".format(i, len(self.results[ledger]), ledger, member, list(self.results[ledger])[0][0]))

    def emptyline(self):
        pass