# Tutorial

_A demonstration video is [available on Youtube](https://www.youtube.com/watch?v=ekFHV5K-Bog)_

---

**Table of Contents**
- [Privledge Daemon](#privledge-daemon)
- [Privledge Shell](#privledge-shell)
- [Getting Started](#getting-started)
	- [Initializing a Ledger](#initializing-a-ledger)
	- [Joining a Ledger](#joining-a-ledger)
- [Adding Blocks to the Ledger](#adding-blocks-to-the-ledger)
- [Generating a Key](#generating-a-key)
- [Displaying the Ledger](#displaying-the-ledger)
- [Nitty Gritty: Protocols](#nitty-gritty-protocols)
	- [UDP Listener](#udp-listener)
	- [TCP Listener](#tcp-listener)
- [To Be Implemented](#to-be-implemented)

---

This project consists of two main components:
* Privledge Daemon
* Privledge Shell

## Privledge Daemon
The daemon maintains the state, including the ledger, all known peers, and any communication threads needed to pass messages to peers.

## Privledge Shell
The shell is your interface to the daemon. In the shell you can interact with the ledger, search for more peers, and more.

## Getting Started
We enter the Privledge shell by the command `pls` after a successful [installation](INSTALL.md):
```
(privledge) $ pls

Welcome to Privledge Shell...
>
```

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

### Initializing a Ledger

We can initialize a ledger with the `init` command, followed by one of the following:
* A base58 encoded RSA public key string
* A path to a public key on the local filesystem
* `gen`, which will generate a public/private RSA key pair. If you also provide a path, it will save the keys to the local filesystem.
```
> init gen

Public Key Hash: 08022ade6757177ad4e0395118cf638b0eabf562
Added key (08022ade6757177ad4e0395118cf638b0eabf562) as a new Root of Trust
root>
```

### Joining a Ledger

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
		Block Hash: d1a57995ecf02bed7c08b546702424ee2fd67a7654c48f2f2f22a7502033be81
		Message: 2TuPVgMCHJy5atawrsADEzjP7MCVbyyCA89UW6Wvjp9HrAsCWKC5L4c1xVjtShQ7
		Message Hash: 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e
		Signatory Hash: 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e (self-signed)
		Predecessor: None

> 
```

The `init` and `join` commands will join us to a ledger. If we would like to leave the ledger, `leave` will remove the ledger from our system and allow us to join another or generate our own:
```
> leave
Left ledger 19991b9288c93cb41a6e042d040383763912fd03e0f6b5c717b42965c0b99a7e
>
```

## Adding Blocks to the Ledger

Only a block signed by a valid key will be accepted onto the ledger. If you are the node that initialized the ledger (with `init`), your private key is already automatically used to sign any new blocks.

The `block` command adds new blocks to the ledger and requires a blocktype (key|revoke|text) followed by a message. To add a new key, the command is

```
root> block key <base58-encoded public key>
Added new block to ledger:

		Type: key
		Block Hash: 1ddafda59d2a6a6be1c4796f1664244341b13fa1b8d2d8255afe316578463e59
		Message: <base58-encoded public key>
		Message Hash: c84e8341fd47b00911f49ae921a247a99603ca2a1f594234279a91892e16ac32
		Signatory Hash: ab8c88feeccf1f108111ae777fc24be76a4b1d2348f564ea2fadabc07f91b0b3
		Predecessor: 66d2e72288cc9299415aa0ee014f2accea3f63f054fbd2e1d7c87e0dfd0f9993

root> 
```

The `revoke` blocktype requires a public key and revokes it from the ledger. `text` blocks simply contain arbitrary text:

```
root> block text hello world!
Added new block to ledger:

		Type: text
		Block Hash: 66d2e72288cc9299415aa0ee014f2accea3f63f054fbd2e1d7c87e0dfd0f9993
		Message: hello world!
		Message Hash: 7509e5bda0c762d2bac7f90d758b5b2263fa01ccbc542ab5e3df163be08e6ca9
		Signatory Hash: ab8c88feeccf1f108111ae777fc24be76a4b1d2348f564ea2fadabc07f91b0b3
		Predecessor: f99e2442950afc5d43a076481510ddb9a9f647baac23f3cf5b2d501b6dd51aa7

root>
```

## Generating a Key

If you need a quick and dirty way to generate an RSA key, `key` will do it for you. 

```
> key gen
<new public key>
> 
```

The `key gen` command generates a public-private key pair and outputs the public portion to the console base58 encoded. You can then copy that and use it to add a new key to the ledger from a node with an authorized private key.

```
root> block key <new public key>
Added new block to ledger:

		Type: key
		Block Hash: 148e395adfd8f3dfe798572eb318c2514a91f255f77636b2dd33168c691c362a
		Message: <new public key>
		Message Hash: de2e233f919c09137f97a113a797cc69b99e34465e5b1d2ea25da6f6bbb09649
		Signatory Hash: d77bf92679bfa82207743a8790c9b266183d480b50c23d69cfd56e44ce20e0a7
		Predecessor: 1ddafda59d2a6a6be1c4796f1664244341b13fa1b8d2d8255afe316578463e59

root>
```

With our key added, we can now write to the ledger as well:

```
> block text I'm a trusted node!
Added new block to ledger:

		Type: text
		Block Hash: 3882d9cd33bb20c4d189c4f717164e1a97ad1d7008287ce3f50616c822a82fa6
		Message: I'm a trusted node!
		Message Hash: 676b9a62c5d772e0d428c2c08074920da49510a94b187bf164049c8ec3daec6f
		Signatory Hash: de2e233f919c09137f97a113a797cc69b99e34465e5b1d2ea25da6f6bbb09649
		Predecessor: 148e395adfd8f3dfe798572eb318c2514a91f255f77636b2dd33168c691c362a

>
```

## Displaying the Ledger

Displaying the ledger is done with the `ledger` command

```
> ledger


13		Type: text
		Block Hash: 3882d9cd33bb20c4d189c4f717164e1a97ad1d7008287ce3f50616c822a82fa6
		Message: I'm a trusted node!
		Message Hash: 676b9a62c5d772e0d428c2c08074920da49510a94b187bf164049c8ec3daec6f
		Signatory Hash: de2e233f919c09137f97a113a797cc69b99e34465e5b1d2ea25da6f6bbb09649
		Predecessor: 148e395adfd8f3dfe798572eb318c2514a91f255f77636b2dd33168c691c362a


12		Type: key
		Block Hash: 148e395adfd8f3dfe798572eb318c2514a91f255f77636b2dd33168c691c362a
		Message: 2TuPVgMCHJy5atawrsADEzjP7MCVbyyCA89UW6Wvjp9HrAUjudRyQEGBjDpD5UH7
		Message Hash: de2e233f919c09137f97a113a797cc69b99e34465e5b1d2ea25da6f6bbb09649
		Signatory Hash: d77bf92679bfa82207743a8790c9b266183d480b50c23d69cfd56e44ce20e0a7
		Predecessor: 1ddafda59d2a6a6be1c4796f1664244341b13fa1b8d2d8255afe316578463e59


11		Type: key
		Block Hash: 1ddafda59d2a6a6be1c4796f1664244341b13fa1b8d2d8255afe316578463e59
		Message: 2TuPVgMCHJy5atawrsADEzjP7MCVbyyCA89UW6Wvjp9HrAibjYGr3FUsSLd5q8yu
		Message Hash: c84e8341fd47b00911f49ae921a247a99603ca2a1f594234279a91892e16ac32
		Signatory Hash: ab8c88feeccf1f108111ae777fc24be76a4b1d2348f564ea2fadabc07f91b0b3
		Predecessor: 66d2e72288cc9299415aa0ee014f2accea3f63f054fbd2e1d7c87e0dfd0f9993


		...10 hidden blocks...

r		Type: key (root)
		Block Hash: 6cbc660069f687426f36bb92a6a1bc8c564ca40f6aa7f81d11f7fa44730b09e2
		Message: 2TuPVgMCHJy5atawrsADEzjP7MCVbyyCA89UW6Wvjp9HrBtr9a3jck5CbJcZbSq1
		Message Hash: ab8c88feeccf1f108111ae777fc24be76a4b1d2348f564ea2fadabc07f91b0b3
		Signatory Hash: ab8c88feeccf1f108111ae777fc24be76a4b1d2348f564ea2fadabc07f91b0b3 (self-signed)
		Predecessor: None


>
```

You may display an arbitrary number of blocks by including a number after the command, such as 

```
> ledger 1


13		Type: text
		Block Hash: 3882d9cd33bb20c4d189c4f717164e1a97ad1d7008287ce3f50616c822a82fa6
		Message: I'm a trusted node!
		Message Hash: 676b9a62c5d772e0d428c2c08074920da49510a94b187bf164049c8ec3daec6f
		Signatory Hash: de2e233f919c09137f97a113a797cc69b99e34465e5b1d2ea25da6f6bbb09649
		Predecessor: 148e395adfd8f3dfe798572eb318c2514a91f255f77636b2dd33168c691c362a


		...12 hidden blocks...

r		Type: key (root)
		Block Hash: 6cbc660069f687426f36bb92a6a1bc8c564ca40f6aa7f81d11f7fa44730b09e2
		Message: 2TuPVgMCHJy5atawrsADEzjP7MCVbyyCA89UW6Wvjp9HrBtr9a3jck5CbJcZbSq1
		Message Hash: ab8c88feeccf1f108111ae777fc24be76a4b1d2348f564ea2fadabc07f91b0b3
		Signatory Hash: ab8c88feeccf1f108111ae777fc24be76a4b1d2348f564ea2fadabc07f91b0b3 (self-signed)
		Predecessor: None


> 
```

The `ledger` command will always show the root of trust in addition to the specified number of blocks.

## Nitty Gritty: Protocols
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
As a proof of concept, this project is a work in progress. The following features are planned but have not yet been implemented:
* **System Integration**: As a proof of concept, it should demonstrate how a system could utilize the ledger as a system access control list.

* **Privledge Levels**: Demonstrate different uses for different privilege levels:

    - root
    - trusted
    - member
