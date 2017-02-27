from privledge import utils


class Ledger():
    def __init__(self, root_public, peers=None):
        self._root_ = root_public
        if peers is None:
            self._peers_ = set()
        else:
            self._peers_ = peers

    def add_peer(self, peer):
        self._peers_.add(peer)

    @property
    def id(self):
        return utils.gen_id(self._root_.exportKey())

    @property
    def pubkey(self):
        return self._root

    @property
    def peers(self):
        return self._peers
