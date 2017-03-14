from privledge import settings
from privledge import PrivledgeShell

# STARTUP
def main():
    # Initialize any global variables
    settings.init()

    # Debug on if argument present
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        settings.debug = True
        print("Debug mode is {}".format(settings.debug))

    # Start up shell
    PrivledgeShell()


if __name__ == '__main__':
    main()
