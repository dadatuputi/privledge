import threading

from privledge import settings
from privledge.privledge_shell import PrivledgeShell
from privledge.privledge_daemon import PrivledgeDaemon

# STARTUP
def start_privledge():
    settings.init()
    # Start up Daemon threads
    daemon_thread = PrivledgeDaemon()
    daemon_thread.start()
    # Start up shell
    prompt = PrivledgeShell(daemon_thread)

if __name__ == '__main__':
    start_privledge()