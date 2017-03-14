from privledge import utils
from privledge import block
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA
import json

class Ledger():


    def __init__(self, root_block):
        self.root = root_block
        self.root.previous = None

        self.len = 0
        self.tail = root_block



    @property
    def id(self):
        return self.root.pubkey_hash



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
                             self.tail.hash)

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
        self.len += 1

    def to_list(self):
        blocklist = []
        self.reverse_list(blocklist, self.tail)
        return blocklist

    def reverse_list(self, list, item):
        if item.previous == None:
            list.append(item)
        else:
            self.reverse_list(list, item.previous)
            list.append(item)
