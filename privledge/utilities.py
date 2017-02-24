from termcolor import cprint
from enum import Enum

class Level(Enum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1

def log_message(message, priority = Level.LOW, force = False):
    # Uses termcolor: https://pypi.python.org/pypi/termcolor
    color = 'green'
    background = 'on_grey'

    global debug

    if priority == Level.LOW:
        color = 'green'
        background = 'on_grey'
    elif priority == Level.MEDIUM:
        color = 'orange'
        background = 'on_grey'
    elif priority == Level.HIGH:
        color = 'red'
        background = 'on_white'

    if debug or force:
        cprint(message, color, background)
