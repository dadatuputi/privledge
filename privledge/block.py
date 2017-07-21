from enum import Enum
import json
import base64
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from privledge import utils


class BlockType(Enum):
    add_key = 0             # message is public key
    revoke_key = 1          # message is public key
    text = 2                # message is text

    def repr_json(self):
        return self.name


class Block:

    def __init__(self, blocktype, predecessor, message, signature=None, signatory_hash=None):
        self.blocktype = blocktype
        self.predecessor = predecessor
        self.message = message
        self.signature = signature
        self.signatory_hash = signatory_hash

    @property
    def message_hash(self):
        if self.blocktype is BlockType.text:
            return None
        else:
            return utils.gen_hash(self.message)

    @property
    def hash(self):
        return SHA256.new(self.__repr__().encode('utf-8'))

    @property
    def hash_body(self):
        """Hash everything but the signature and signatory hash"""

        return SHA256.new(self.body.encode('utf-8'))

    @property
    def body(self):
        """This generates a json string for signing; excludes signature fields"""

        body = {k:v for k,v in self.__dict__.items() if k != 'signature' and k != 'signatory_hash'}
        return json.dumps(body, cls=utils.ComplexEncoder, sort_keys=True)

    @property
    def signature_decoded(self):
        return base64.b64decode(self.signature)

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
        # Generate public key and hash from the private key
        pubkey = privkey.publickey()
        pubkey_hash = utils.gen_hash(pubkey.exportKey())

        # Sign the block body hash
        h = SHA256.new(self.body.encode())
        signer = PKCS1_v1_5.new(privkey)

        # Set the block signature values
        self.signature = base64.b64encode(signer.sign(h))
        self.signatory_hash = pubkey_hash

        # Validate our signature is correct
        if not self.validate(pubkey):
            self.signature = None
            self.signatory_hash = None

            raise RuntimeError("Could not sign the block - signature validation failed")

    def validate(self, pubkey):
        """Validate this block's signature with the supplied public key"""

        signer = PKCS1_v1_5.new(pubkey)
        return signer.verify(SHA256.new(self.body.encode()), self.signature_decoded)

    def __str__(self):
        return '\tType: {}{}\n' \
               '\tMessage: {}\n' \
               '\tMessage Hash: {}\n' \
               '\tSignatory Hash: {}{}'\
            .format(self.blocktype.name, ' (root)' if self._is_root else '',
                    self.message.decode()[:60].replace('\n', '')+'...',
                    self.message_hash,
                    self.signatory_hash, ' (self-signed)' if self.is_self_signed else '')

    def __repr__(self):
        return json.dumps(self.__dict__, cls=utils.ComplexEncoder, sort_keys=True)

    def repr_json(self):
        return self.__dict__