from cmd import Cmd
from sshpubkeys import SSHkey

class PrivledgeShell(Cmd):

    def do_init(self, args):
        """Initialize the ledger with a provided Root of Trust (RSA Public Key)"""
        if len(args) == 0: