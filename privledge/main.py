from privledge import settings
from privledge import PrivledgeShell

# STARTUP
def start_privledge():
    # Initialize any global variables
    settings.init()

    # Start up shell
    PrivledgeShell()


if __name__ == '__main__':
    start_privledge()
