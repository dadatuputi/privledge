DISCOVERY_TIMEOUT = 1
BIND_IP = ''
BIND_PORT = 2525

# Messaging Defaults
MSG_SIZE_BYTES = 4
MSG_TYPE_HB = 'hb'
MSG_TYPE_DISCOVER = 'discover'
MSG_TYPE_JOIN = 'join'
MSG_TYPE_PEER = 'peers'
MSG_TYPE_LEDGER = 'ledger'
MSG_TYPE_SUCCESS = '200'
MSG_TYPE_FAILURE = '404'
MSG_HB_FREQ = 10 # Minimum time in seconds between HB checks to peers
MSG_HB_TTL = 10*MSG_HB_FREQ  # Minimum time in seconds for HB to determine peer is dead
MSG_HB_TIMEOUT = 3 # Time in seconds for a hb messsage to timeout

def init():
    global debug
    debug = False

