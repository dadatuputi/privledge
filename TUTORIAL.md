# Tutorial
This project consists of two main components:
* Privledge Daemon
* Privledge Shell

## Privledge Daemon
The daemon maintains the state, including the ledger, all known peers, and any communication threads needed to pass messages to peers.

## Privledge Shell
The shell is your interface to the daemon. In the shell you can interact with the ledger, search for more peers, and more.

Typing `help` within the shell will show all the available commands:

```
> help

Documented commands (type help <topic>):
========================================
block  discover  help  join  leave   quit   status
debug  exit      init  key   ledger  shell
```

Typing `help <command name>` will give specific help for that command:

```
> help key
Manage your local private key

        Arguments:
        gen: Generate a new RSA key
        pub (default): Prints the public key
        priv: Prints the private key
        
> 
```


## Getting Started
We enter the Privledge shell by the command `pls` after a successful [installation](INSTALL.md):
```
(privledge) $ pls

Welcome to Privledge Shell...
>
```

We can initialize a ledger with the `init` command, followed by one of the following:
* A base58 encoded RSA public key string
* A path to a public key on the local filesystem
* `gen` will generate a public/private RSA key pair. If you also provide a path, it will save the keys to the local filesystem.
```
> init gen

Public Key Hash: 08022ade6757177ad4e0395118cf638b0eabf562
Added key (08022ade6757177ad4e0395118cf638b0eabf562) as a new Root of Trust
>
```

If we would like to join an existing ledger, we use the `discover` command to search our local subnet for available ledgers, or `discover <ip>` to query a specific ip address:
```
> discover
Found 2 available ledgers
1 | 192.168.159.131: (1 members) 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e 
2 | 192.168.159.130: (1 members) 812858c1fd8fcb38cd8fa3f8c1040dae06714a78822818c3b7a48eb8b66ced16 
>
```

If we see a ledger we would like to join, we use the `join` command, followed by the number of the item provided by the `list` command:
```
> join 1
Joined ledger 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e
>
```

To see the status of our ledger, we can use the `status` command:
```
> status
You are a member of ledger 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e and connected to 1 peers.
>
```

`status detail` gives us more details about our ledger; the Root of Trust:

```
> status detail
You are a member of ledger 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e and connected to 1 peers.

Root of Trust:
		Type: key (root)
		Predecessor: None
		Message: 2TuPVgMCHJy5atawrsADEzjP7MCVbyyCA89UW6Wvjp9HrAsCWKC5L4c1xVjtShQ7
		Message Hash: 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e
		Signatory Hash: 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e (self-signed)
		Block Hash: d1a57995ecf02bed7c08b546702424ee2fd67a7654c48f2f2f22a7502033be81
> 

```

The `init` and `join` commands will join us to a ledger. If we would like to leave the ledger, `leave` will remove the ledger from our system and allow us to join another or generate our own:
```
> leave
Left ledger 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e
>
```

## Protocols
Privledge uses both TCP and UDP to communicate between peers. 
Once a ledger is established by the daemon, the daemon spawns a listener on port 2525 for each protocol:


### UDP Listener
The UDP Listener listens for ledger queries and responds with a hash of the root of trust public key. This is the ledger `id` and serves to identify the ledger.

The UDP Listener also listens for heartbeat messages. Heartbeat messages contain a ledger id - if the heartbeat ledger id is the same as our ledger id we consider the source a peer and add them to the daemon peer list along with the current time.

In addition to keeping the peer list alive, these heartbeat messages help keep the ledger in sync. Each heartbeat contains the hash of the last block in the chain - if it matches our tail hash, we are in sync and do nothing. If it is in our ledger, the peer is out of sync and we do nothing. If it is not in our ledger we initiate a ledger sync, detailed below. 

An additional thread, UDP Heartbeat, regularly loops through the list of peers and sends heartbeat messages. It also maintains the peer list by pruning away peers it hasn't received a heartbeat from in some time.

### TCP Listener
The TCP Listener accepts sockets and spawns threads that manage different message types. TCP messages are of the following types:

* `join` : This message contains a block hash. If it matches the ledger id, the receiver will respond with the entire public key of the root of trust
* `ledger` : This message contains a block hash. The receiver will respond with a list of blocks up to the specified block hash. If the block hash is null, the entire ledger will be transmitted. This message type allows for synchronization between nodes.
* `peers` : This message is used to request the list of peers from the another peer. The receiver replies with a list of its peers.

## To Be Implemented:
As a proof of concept, this project is a work in progress. The following features have yet to be implemented for this to be considered a 'functional' proof of concept:
* **System Integration**: As a proof of concept, it must demonstrate how a system could utilize the ledger to 'whitelist' console access, for example.

* **Privledge Levels**: Demonstrate different uses for the different authorities:

    - root
    - trusted
    - member
