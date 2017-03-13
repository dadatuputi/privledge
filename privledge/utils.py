from termcolor import cprint
from enum import Enum
from privledge import settings
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA

import os.path
from os import chmod


class Level(Enum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1


def log_message(message, priority = Level.LOW, force = False):
    # Uses termcolor: https://pypi.python.org/pypi/termcolor
    color = 'green'
    background = 'on_grey'

    if priority == Level.LOW:
        color = 'green'
        background = 'on_grey'
    elif priority == Level.MEDIUM:
        color = 'yellow'
        background = 'on_grey'
    elif priority == Level.HIGH:
        color = 'red'
        background = 'on_white'

    if settings.debug or force:
        cprint(message, color, background)

def get_key(message=None):

    # Check for RSA key
    if message is not None:
        try:
            key = RSA.importKey(message.strip())
            return key
        except Exception as err:
            message = "Could not parse {0} as an RSA key: {1}".format(message, err)

            # Let's try to parse the message as a path
            if os.path.isfile(message):
                message = "{0} is a valid path.".format(message)
                # Read given file
                with open(message) as message_file:
                    message_contents = message_file.read()

                try:
                    key = RSA.importKey(message_contents.strip())
                    return key
                except Exception as err:
                    message = "Could not parse file {0} as an RSA key: {1}".format(message, err)

            else:
                message = "Could not parse {0} as valid path.".format(message)

    # Key is None
    # Log error and return
    log_message(message)
    return None



def generate_openssh_key(save=False, filename='id_rsa', location='', keylength=2048):
    log_message("Generating {0}-bit RSA key".format(keylength))

    key = RSA.generate(keylength)

    if save:
        with open("{0}{1}".format(location, filename), 'w') as content_file:
            chmod("{0}{1}".format(location, filename), 0o0600)
            content_file.write(key.exportKey('PEM'))
        with open("{0}{1}.pub".format(location, filename), 'w') as content_file:
            content_file.write(key.publickey().exportKey('OpenSSH'))

    return key

def gen_hash(message):
    h = SHA.new()
    h.update(message)
    return h.hexdigest()


def append_len(message):
    return str(len(message)).zfill(settings.MSG_SIZE_BYTES) + message


