from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256


class Ledger:

    def __init__(self):
        self.len = 0
        self.tail = None
        self.root = None

    @property
    def id(self):
        return self.root.message_hash

    def find_message(self, hash):
        current = self.tail

        while current:
            if current.message_hash == hash:
                return current
            else:
                current = current.previous

        return ValueError('The key was not found in the ledger', hash)

    def append(self, block):

        # Adding root?
        if block.predecessor is None and self.root is None:
            self.root = block

        # Do some checks to make sure block is correctly formed
        else:

            # Ensure the hash is correct
            if not block.predecessor == self.tail.hash:
                raise ValueError('Predecessor hash does not match the last accepted block', block.predecessor,
                                 self.tail.hash)

            # Find the signatory key in our ledger
            signatory = self.find_message(block.signatory_hash)
            signatory_key = RSA.importKey(signatory)

            # Verify the signature is valid
            h = SHA256.new(block.body)
            verifier = PKCS1_PSS.new(signatory_key)
            if not verifier.verify(h, block.signature):
                raise ValueError('The block signature is not valid', block.signature, signatory)

        # Hash is correct, Signatory Exists, Signature is Valid: Add to ledger!
        block.previous = self.tail
        self.tail = block
        self.len += 1

    def to_list(self, predecessor=None):
        blocklist = []
        self.reverse_list(blocklist, self.tail, predecessor)
        return blocklist

    def reverse_list(self, list, item, predecessor):
        if item.predecessor is None and predecessor is not None:
            # We got a bogus predessor, return None list
            list = None
        elif item.predecessor == predecessor:
            list.append(item)
        else:
            self.reverse_list(list, item.previous, predecessor)
            if list is not None:
                list.append(item)
