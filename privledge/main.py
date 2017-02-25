from privledge import settings
from privledge import PrivledgeShell
from privledge import PrivledgeDaemon


# STARTUP
def start_privledge():
    # Initialize any global variables
    settings.init()

    # Start up Daemon threads
    daemon = PrivledgeDaemon()

    # Start up shell
    PrivledgeShell(daemon)


if __name__ == '__main__':
    start_privledge()
