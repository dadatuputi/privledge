import base58
import json
import textwrap
from enum import Enum

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA


from privledge import utils


class BlockType(Enum):
    key = 0         # message is public key
    revoke = 1      # message is public key
    text = 2        # message is text

    def repr_json(self):
        return self.name

class Block:
    def __init__(self, blocktype, predecessor, message, signature=None, signatory_hash=None):
        self.blocktype = blocktype
        self.predecessor = predecessor
        self.message = message
        self.signature = signature
        self.signatory_hash = signatory_hash

    # message_hash is used primarily for key lookup
    @property
    def message_hash(self):
        return utils.gen_hash(self.message)

    @property
    def hash(self):
        return utils.gen_hash(self.__repr__())

    @property
    def hash_body(self):
        """Hash everything but the signature and signatory hash"""
        return utils.gen_hash(self.body)

    @property
    def body(self):
        """This generates a json string for signing; excludes signature fields"""

        body = {k: v for k, v in self.__dict__.items() if
                k != 'signature' and k != 'signatory_hash' and k != 'ptr_previous'}
        return json.dumps(body, cls=utils.ComplexEncoder, sort_keys=True)

    # @property
    # def signature_decoded(self):
    #     return base64.b64decode(self.signature)

    @property
    def is_signed(self):
        return self.signature is not None and self.signatory_hash is not None

    @property
    def is_self_signed(self):
        return self.message_hash == self.signatory_hash

    @property
    # This is an insecure check
    def _is_root(self):
        return self.predecessor is None and self.is_self_signed

    def sign(self, privkey):
        # Sign the block body hash
        h = SHA256.new(self.body.encode('utf-8'))
        signer = PKCS1_v1_5.new(privkey)

        # Set the block signature values
        self.signature = utils.encode(signer.sign(h))
        self.signatory_hash = utils.gen_hash(utils.encode_key(privkey))

        # Validate our signature is correct
        if not self.validate(privkey.publickey()):
            self.signature = None
            self.signatory_hash = None

            raise RuntimeError("Could not sign the block - signature validation failed")

    def validate(self, pubkey):
        """Validate this block's signature with the supplied public key"""

        # If pubkey is a string, turn it into a key object
        if isinstance(pubkey, str):
            pubkey = RSA.importKey(utils.decode(pubkey))

        signer = PKCS1_v1_5.new(pubkey)
        return signer.verify(SHA256.new(self.body.encode('utf-8')), utils.decode(self.signature))

    def __str__(self):
        return '\t\tType: {}{}\n' \
               '\t\tPredecessor: {}\n' \
               '\t\tMessage: {}\n' \
               '\t\tMessage Hash: {}\n' \
               '\t\tSignatory Hash: {}{}\n' \
               '\t\tBlock Hash: {}' \
            .format(self.blocktype.name, ' (root)' if self._is_root else '',
                    'None' if self._is_root else utils.hash_color(self.predecessor),
                    self.message[:64],
                    utils.hash_color(self.message_hash),
                    utils.hash_color(self.signatory_hash), ' (self-signed)' if self.is_self_signed else '',
                    self.hash)

    def __repr__(self):
        body = {k: v for k, v in self.__dict__.items() if k != 'ptr_previous'}
        return json.dumps(body, cls=utils.ComplexEncoder, sort_keys=True)

    def repr_json(self):
        return self.__dict__

