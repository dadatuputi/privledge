# Privledge Installation

## Recommendation
_Privledge uses Python 3.5 so be sure to use the appropriate command for Python 3.5 pip_

I recommend using a virtual environment with mkproject ([documentation](http://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html)):
```
$ mkproject -p python3.5 privledge
```
To enter and leave your virtual environment, use the commands `workon` and `deactivate` respectively:
```
$ workon privledge
(privledge) $ deactivate
$
```

## From Source
You need the Python 3.5 headers (available in the python3.5-dev package on Ubuntu)
```
(privledge) $ git clone git@github.com:elBradford/privledge.git .
(privledge) $ pip install -e .
(privledge) $ pls
```
`-e` is an optional pip argument that allows you to modify the code and have the changes immediately applied to the installed script - no need to reinstall to see changes you  made.

## From PyPI
TODO: _Not yet uploaded to Pip repository_
```
(privledge) $ pip install privledge
(privledge) $ pls
```

# Usage
This proof-of-concept code centers around two main components:
* Privledge Shell
* Privledge Daemon

## Privledge Shell
This is your interface to everything that runs in the background. `help` will show all the commands available.

## Privledge Daemon
This module maintains the ledger, all known peers, and any communication threads needed to pass messages to peers.

## Getting Started
We begin by starting `pls` after it has been installed (see above):
```
(privledge) $ pls

Welcome to Privledge Shell...
>
```

We can initialize a ledger with the `init` command, followed either by a RSA public key string, or a path to a public key file. Using the `init generate` command will generate a public/private RSA key pair. If you also provide a path, it will save the keys to the local filesystem.
```
> init generate

Public Key Hash: 08022ade6757177ad4e0395118cf638b0eabf562
Added key (08022ade6757177ad4e0395118cf638b0eabf562) as a new Root of Trust
>
```

If we would like to join an existing ledger, we can use the `list` command to search our local subnet for available ledgers, or `list <ip>` to query a specific ip address:
```
> list
Searching for available ledgers for 10 seconds...
Found 1 available ledgers
1 | 192.168.159.129: (1 members) ccee4bcc68631ee2c8905d4600c1a1432818db00
>
```

If we see a ledger we would like to join, we use the `join` command, followed by the number of the item provided by the `list` command:
```
> join 1
Joined ledger ccee4bcc68631ee2c8905d4600c1a1432818db00
>
```

To see the status of our ledger, we can use the `status` command:
```
> status
You are a member of ledger ccee4bcc68631ee2c8905d4600c1a1432818db00 with 1 peers.
>
```

`status detail` gives us more details about our ledger:

```
You are a member of ledger ccee4bcc68631ee2c8905d4600c1a1432818db00 with 1 peers.

Root of Trust:
	Type: root
	Key Hash: ccee4bcc68631ee2c8905d4600c1a1432818db00
	Signatory Hash: ccee4bcc68631ee2c8905d4600c1a1432818db00
>
```

The `init` and `join` commands will join us to a ledger. If we would like to leave the ledger, `leave` will remove the ledger from our system and allow us to join another or generate our own:
```
> leave
Left ledger ccee4bcc68631ee2c8905d4600c1a1432818db00
>
```

## Protocols
This proof of concept uses several primitive protocols to communicate between peers. Once a ledger is established (either joined or initialized), two listeners are spawned on port 2525, respectively:

* TCP Listener
* UDP Listener

### UDP Listener
The UDP Listener listens for ledger queries, and responds with a hash of the root of trust public key. This is the ledger `id` and serves to identify the ledger.

The UDP Listener also listens for heartbeat messages with a matching ledger id and adds them to its peer list with the current time.

An additional thread, UDP Heartbeat, regularly loops through the list of peers and sends heartbeat messages. It also maintains the peer list by pruning away peers it hasn't received a heartbeat from in some time.

### TCP Listener
The TCP Listener accepts sockets and spawns threads that manage different message types. TCP messages are of the following types:

* `join` : This message contains a block hash. If it matches the ledger id, the receiver will respond with the entire public key of the root of trust
* `ledger` : This message contains a block hash. The receiver will respond with a list of blocks up to the specified block hash. If the block hash is null, the entire ledger will be transmitted. This message type allows for synchronization between nodes
* `peers` : This message simply requests the list of peers from the receiver. The receiver replies with a list of its peers.

## To Be Implemented:
As a proof of concept, this project is a work in progress. The following features have yet to be implemented for this to be considered a 'functional' proof of concept:

* **Gossip Protocol**: This protocol is necessary to maintain

    - Accurate ledger synchronization between peers
    - Accurate peer list synchronization between peers
    - New block propegation throughout peers

* **System Integration**: As a proof of concept, it must demonstrate how a system could utilize the ledger to 'whitelist' console access, for example.

* **Privledge Levels**: Demonstrate different uses for the different authorities:

    - root
    - trusted
    - member
