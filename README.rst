Privledge
======
**Privledge** is a proof-of-concept private, privleged ledger used for public key management written in python.

#### Screenshot
![Screenshot software](http://url/screenshot-software.png "screenshot software")

## Download
* [Version 0.1](https://github.com/elBradford/privledge/archive/master.zip)
* Other Versions

## Usage
```$ git clone https://github.com/elBradford/privledge.git
...```

## License
* see [LICENSE](https://github.com/elBradford/privledge/blob/master/LICENSE.md) file

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
'''
$ pip install privledge
$ pls
'''

# Usage
This proof-of-concept code centers around two main components:
* Privledge Shell
* Privledge Daemon

## Privledge Shell
This is your interface to everything that runs in the background. `help` will show all the commands available.

## Privledge Daemon
This module maintains the ledger, all known peers, and any communication threads needed to pass messages to peers.

## Getting Started
We begin by starting pls after it has been installed (see above):
```
$ pls

Welcome to Privledge Shell...
>
```

We can use the `list` command to search our local subnet for available ledgers, or `list <ip>` to query a specific ip address:
```
> list
