from enum import IntEnum
import hashlib
import json
from Crypto.Signature import PKCS1_PSS
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from privledge import utils




class BlockType(IntEnum):
    root = 0
    trusted = 1
    member = 2


class Block():

    def __init__(self, type, predecessor, pubkey, pubkey_hash):
        self.type = type
        self.predecessor = predecessor
        self.pubkey = pubkey
        self.pubkey_hash = pubkey_hash
        self.signature = None
        self.signatory_hash = None

    @property
    def hash(self):
        return hashlib.sha1(self)

    @property
    def hash_body(self):
        # Hash everything but the signature and signatory hash
        return hashlib.sha1(self.body)

    @property
    def body(self):
        '''This generates a json string for signing; excludes signature fields'''
        body = {k:v for k,v in self.__dict__.items() if k != 'signature' and k != 'signatory_hash'}
        return json.dumps(body, default=self.serialize, sort_keys=True)



    def sign(self, privkey, pubkey_hash):
        key = RSA.importKey(privkey)
        body = self.body
        h = SHA.new(self.body.encode())
        signer = PKCS1_PSS.new(key)
        self.signature = signer.sign(h)
        self.signatory_hash = pubkey_hash



    def __str__(self):
        return '\tType: {0}\n\tKey Hash: {1}\n\tSignatory Hash: {2}'.format(self.type.name, self.pubkey_hash, self.signatory_hash)

    def __repr__(self):
        return json.dumps(self.__dict__, default=self.serialize, sort_keys=True)

    def serialize(self, obj):
        """JSON Serializer for objects in Block"""

        if isinstance(obj, BlockType):
            return obj.name
        elif isinstance (obj, bytes):
            return obj.decode('ascii')