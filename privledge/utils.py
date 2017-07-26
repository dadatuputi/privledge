from termcolor import cprint
from enum import Enum
from privledge import settings
from privledge import messaging
from privledge import block
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256

import os.path
import json
from os import chmod


class Level(Enum):
    LOW = 3         # Used for repeating messages (eg heartbeat)
    MEDIUM = 2      # Use this level for low priority logs (messaging, etc)
    HIGH = 1        # Use this level for typical debug logging such as errors, spawning threads, and state change
    FORCE = 0       # Use this level to force printing - useful for errors affecting ledger state


def log_message(message, debug=Level.HIGH):
    """Log a message - use this function to do any printing to the console. From lowest priority:
    LOW: Use for repeating messages (eg heartbeat)
    MEDIUM: Use for low priority (eg messaging)
    HIGH (default): Use for typical debug logging such as errors, state change, thread spawning, etc
    FORCE: Force printing. Use to print to console regardless of debug state or for errors affecting ledger state"""

    if settings.debug >= debug.value:
        # Uses termcolor: https://pypi.python.org/pypi/termcolor
        color = 'green'
        background = 'on_grey'

        if debug == Level.MEDIUM:
            color = 'green'
            background = 'on_grey'
        elif debug == Level.HIGH:
            color = 'yellow'
            background = 'on_grey'
        elif debug == Level.FORCE:
            color = 'red'
            background = 'on_white'

        cprint(message, color, background)


def get_key(key=None):

    # Check for RSA key
    if key is not None:
        try:
            key = RSA.importKey(key.strip())
            return key
        except Exception as err:
            key = "Could not parse {0} as an RSA key: {1}".format(key, err)

            # Let's try to parse the message as a path
            if os.path.isfile(key):
                key = "{0} is a valid path.".format(key)
                # Read given file
                with open(key) as message_file:
                    message_contents = message_file.read()

                try:
                    key = RSA.importKey(message_contents.strip())
                    return key
                except Exception as err:
                    err_msg = "Could not parse file {0} as an RSA key: {1}".format(key, err)

            else:
                err_msg = "Could not parse {0} as valid path.".format(key)

    # Key is None
    # Log error and return
    log_message(err_msg)
    return None


def privkey_generate(save=False, filename='id_rsa', location='', keylength=2048):
    log_message("Generating {0}-bit RSA key".format(keylength))

    key = RSA.generate(keylength)

    if save:
        with open("{0}{1}".format(location, filename), 'w') as content_file:
            chmod("{0}{1}".format(location, filename), 0o0600)
            content_file.write(key.exportKey())
        with open("{0}{1}.pub".format(location, filename), 'w') as content_file:
            content_file.write(key.publickey().exportKey())

    return key


def gen_hash(message):
    if isinstance(message, str):
        h = SHA256.new(message.encode('utf-8'))
    else:
        h = SHA256.new(message)

    return h.hexdigest()


def append_len(message):
    return str(len(message)).zfill(settings.MSG_SIZE_BYTES) + message


def message_decoder(obj):
    if 'msg_type' in obj and 'msg' in obj:
        return messaging.Message(obj['msg_type'], obj['msg'])
    elif 'blocktype' in obj and 'signature' in obj:
        return block.Block(block.BlockType[obj['blocktype']], obj['predecessor'], obj['message'], obj['signature'], obj['signatory_hash'])
    return obj


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):          # Handle bytes
            return obj.decode('ascii')
        if hasattr(obj, 'repr_json'):        # Use object repr_json method
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)


# https://stackoverflow.com/a/529466/1486966
def reverse_enumerate(L):
   for index in reversed(range(len(L))):
      yield index, L[index]
