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
    LOW = 2
    HIGH = 1
    FORCE = 0


def log_message(message, debug=Level.LOW):

    if settings.debug >= debug.value:
        # Uses termcolor: https://pypi.python.org/pypi/termcolor
        color = 'green'
        background = 'on_grey'

        if debug == Level.LOW:
            color = 'green'
            background = 'on_grey'
        elif debug == Level.HIGH:
            color = 'yellow'
            background = 'on_grey'
        elif debug == Level.FORCE:
            color = 'red'
            background = 'on_white'

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
    if 'message_type' in obj and 'message' in obj:
        return messaging.Message(obj['message_type'], obj['message'])
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
