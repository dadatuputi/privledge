from privledge import utils
from privledge import block
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA

class Ledger():


    def __init__(self, root_block):
        self._root = root_block
        self._len = 0



    @property
    def id(self):
        return self._root.pubkey_hash

    @property
    def tail(self):
        return self._tail

    @property
    def root(self):
        return self._root

    @property
    def len(self):
        return self._len



    def find_key(self, hash):
        current = self.tail

        while current:
            if current.pubkey_hash == hash and current.type == block.BlockType.root or current.type == block.BlockType.trusted:
                return current
            else:
                current = current.previous

        return ValueError('The key was not found in the ledger', hash)

    def append(self, block):

        # Ensure the hash is correct
        if not block.predecessor == self.tail.hash:
            raise ValueError('Predecessor hash does not match the last accepted block', block.predecessor,
                             self._tail.hash)

        # Find the signatory key in our ledger
        signatory = self.find_key(block.signatory_hash)
        signatory_key = RSA.importKey(signatory)

        # Verify the signature is valid
        h = SHA.new(block.body)
        verifier = PKCS1_PSS.new(signatory_key)
        if not verifier.verify(h, block.signature):
            raise ValueError('The block signature is not valid', block.signature, signatory)

        # Hash is correct, Signatory Exists, Signature is Valid: Add to ledger!
        block.previous = self.tail
        self.tail = block
        self._len += 1

