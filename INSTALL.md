# Privledge Installation

## Environment Recommendations
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

## Install from Github
```
(privledge) $ git clone git@github.com:elBradford/privledge.git .
(privledge) $ pip install -e .
(privledge) $ pls
```
`-e` is an optional pip argument that allows you to modify the code and have the changes immediately applied to the installed script - no need to reinstall to see changes you  made.

#### [Continue to the Tutorial](TUTORIAL.md)