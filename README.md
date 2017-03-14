Privledge
======
**Privledge** is a proof-of-concept private, privleged ledger used for public key management written in python.

#### Screenshot
![Screenshot software](http://url/screenshot-software.png "screenshot software")

## Download
* [Version 0.1](https://github.com/elBradford/privledge/archive/master.zip)
* Other Versions

## Usage
```
$ git clone https://github.com/elBradford/privledge.git
```

## License
* TBD

## Version
* Version 0.1

# Installation
## From Source
```
$ git clone https://github.com/elBradford/privledge.git
$ cd privledge
$ pip install -e .
$ pls
```
`-e` is optional and allows you to modify the code and have the changes immediately applied to the installed script (no need to reinstall to see changes).

## From Pip
_Not yet uploaded to Pip repository_
```
$ pip install privledge
$ pls
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
$ pls

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
