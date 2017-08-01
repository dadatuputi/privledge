from cmd import Cmd
from privledge import utils
from privledge import settings
from privledge import daemon
from privledge import block
from datetime import datetime

import socket
import os


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
            if args_list[0].lower() == "gen":
                # Generate an RSA key

                if len(args_list) == 1:
                    # Generate a RSA key in memory
                    privkey = utils.gen_privkey()
                else:
                    # Generate and save RSA key
                    privkey = utils.gen_privkey(True, args_list[0])

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
        utils.log_message("Added key ({0}) as a new Root of Trust".format(hash), utils.Level.FORCE)

        self.update_prompt()

    def do_debug(self, args):
        """Sets printing of debug information, valid options are 0-3"""

        try:
            number = int(args)

            # Check for valid number
            if number < 0 or number > len(utils.Level)-1:
                raise ValueError("Out of Bounds Error")
            else:
                settings.debug = number
        except ValueError as e:
            print("{}\nYou did not provide a valid number (0-{}): '{}'".format(e, len(utils.Level)-1, args))

        print("Debug is set to {} ({})".format(settings.debug, utils.Level(settings.debug).name))

        self.update_prompt()

    def do_quit(self, args):
        """Quits the shell"""

        print("Quitting")
        raise SystemExit

    def do_discover(self, args):
        """Attempt to discover other ledgers.

        Arguments:
        peers: include to discover peers on the same ledger and add them to your peer list
        cached: include to utilize the cache
        ip: provide an ip address otherwise the local broadcast will be used.
        """

        args = args.lower().strip().split()

        peers = False
        cached = False
        ip = '<broadcast>'

        # Parse the arguments
        if 'peers' in args:
            # Check that we're even a member of a ledger
            if daemon.ledger is None or daemon.ledger.id is None:
                print("You may not search for peers without being a member of a ledger.")
                return
            peers = True
            args.remove('peers')
        if 'cached' in args:
            cached = len(daemon.disc_peers)>0 if peers else len(daemon.disc_ledgers)
            args.remove('cached')
            utils.log_message("Using cached results" if cached else "Bypassing cache because no results in cache.")
        if len(args) > 0:
            # If we still have arguments, we assume it's an IP address
            ip = args[0]

            # Check for a valid IP
            try:
                socket.inet_pton(socket.AF_INET, ip)
            except socket.error:
                print("You entered an invalid IP address")
                return

        # Get results of discovery and process
        if not cached:
            daemon.disc_ledgers = daemon.discover(ip)

            if peers:
                # If we're looking for peers, we're only looking for ledger ids that match ours
                daemon.disc_peers = daemon.disc_ledgers.get(daemon.ledger.id, set())

        # Display the results
        if peers:
            print("Found {} peers".format(str(len(daemon.disc_peers))))
            if len(daemon.disc_peers) > 0:
                added_peer_count = 0
                for idx, addr in enumerate(daemon.disc_peers):
                    is_peer = addr[0] in daemon.peers
                    print("{} | {}{}"
                          .format(idx+1, '(peer) ' if is_peer else '', addr[0]))

                    # Add non-peers to peer list
                    if not is_peer:
                        daemon.peers[addr[0]] = datetime.now()
                        added_peer_count += 1

                    print("Added {} peers to peer list".format(added_peer_count))

        else:
            print("Found {} available ledgers".format(str(len(daemon.disc_ledgers))))
            if len(daemon.disc_ledgers) > 0:
                member = ''
                for idx,ledger in enumerate(daemon.disc_ledgers):
                    if daemon.ledger is not None and daemon.ledger.id == ledger.strip():
                        member = '(peer)'
                    else:
                        member = ''
                    print("{0} | {4}: ({1} members) {2} {3}".format(idx+1, len(daemon.disc_ledgers[ledger]), ledger, member,
                                                                    list(daemon.disc_ledgers[ledger])[0][0]))

    def do_join(self, args):
        """Join a ledger previously identified by the list command"""

        # Check for no arguments
        if len(args) == 0:
            print("You must provide a ledger number. Use the `discover` command to show ledger numbers.")
            return

        # Check for a valid argument (is integer)
        number = 0
        try:
            number = int(args)

            # Check for valid argument (is valid ledger)
            if number < 0 or number > len(daemon.disc_ledgers):
                raise ValueError("Out of Bounds Error")
        except ValueError as e:
            print("{0}\nYou did not provide a valid number: '{1}'".format(e, args))
            return

        # Pass the daemon the hash and members
        daemon.join_ledger(list(daemon.disc_ledgers.keys())[number-1], list(list(daemon.disc_ledgers.values())[number-1])[0])

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
        """Print the ledger

        Arguments:
        num (default 3): print the last n blocks. If num = 0, print entire ledger
        """

        n = 3
        ledger_list = None

        # Parse arguments
        try:
            if len(args) > 0:
                n = int(args)
        except ValueError:
            print("If you provide an argument, provide a valid integer")
            return

        ledger_list = daemon.ledger.list[-n:]

        # Prepare iterator
        revers_iter = None
        if n <= 0 or n >= len(daemon.ledger.list) - 1:
            reverse_iter = range(len(daemon.ledger.list)-1, -1, -1)
        else:
            reverse_iter = range(len(daemon.ledger.list) - 1, len(daemon.ledger.list) - 1 - n, -1)

        print('\n')

        # Print each block in reverse order
        for i in reverse_iter:
            print('r' if i is 0 else i, end='')
            print(daemon.ledger.list[i])
            print('\n')

        # Check to ensure root was printed
        if 0 not in reverse_iter:
            print('\t\t...{} hidden blocks...\n'.format(len(daemon.ledger.list) - len(reverse_iter) - 1))
            print('r', end='')
            print(daemon.ledger.root)
            print('\n')

    def do_block(self, args):
        """Add a block to the ledger.

        Command: block blocktype message

        Arguments:
        blocktype: key|revoke|text
        message: based on blocktype, may be public key or arbitrary text

        eg: block key MIIEpAIBAAKCAQEAxWLpWMCgNDXmN/G+w3bRiunslFoGDiZzYx1C0i...
        """

        args = args.split()
        if len(args) < 2:
            print("You must provide the blocktype and message to create a block")
            return
        elif daemon.privkey is None:
            print("You must have a private key added before you may create a block")
            return
        elif not daemon.joined():
            print("You must be joined to a ledger in order to add a block. Try 'init'")
            return

        blocktype = args[0].lower()
        message = ' '.join(args[1:])

        try:

            blocktype = block.BlockType[blocktype]

            new_block = block.Block(blocktype, daemon.ledger.tail.hash, message)
            new_block.sign(daemon.privkey)

            daemon.ledger.append(new_block)
            print("Added new block to ledger:")
            print('\n{}\n'.format(new_block))

        except KeyError as e:
            print("Could not add block: {} is not a valid blocktype".format(e))
        except ValueError as e:
            print("Could not add block: {}".format(e))

    def do_key(self, args):
        """Manage your local private key

        Arguments:
        gen: Generate a new RSA key
        pub (default): Prints the public key
        priv: Prints the private key
        """

        args = args.lower()

        if len(args) <= 0 or args == 'pub':
            if daemon.privkey is not None:
                print(utils.encode_key(daemon.privkey))
            else:
                print("You don't have a key to display")
        elif args == 'priv':
            print(utils.encode_key(daemon.privkey, public=False))
        elif args == 'gen':
            daemon.privkey = utils.gen_privkey()
            self.do_key('')
        else:
            print("Unknown argument(s): {}".format(args))

    def update_prompt(self):
        """Update the prompt based on system variables"""

        indicators = []

        if daemon.is_root():
            indicators.append('root')
        if settings.debug > 0:
            indicators.append('debug({})'.format(settings.debug))

        self.prompt = '|'.join(indicators) + '> '

    def emptyline(self):
        pass