Spittalpond
===========
<!-- The closest Bermuda's got to an Oasis! -->

What is it?
-----------

Spittalpond is an Python interface for the Oasis Django API webservices.
It acts as a front-end that allows you to run models, exposures and other
useful webservices in Oasis.
Effectively, it's turns you Oasis style .csv files into useful GUL data!

Installation
------------

You can quickly install this package by downloading the code and running the
following commands:

``` sh
$ cd path/to/spittalpond
$ python setup.py install
```

Usage
-----

Spittalpond can be quickly run by using the config interface. Note that you will
have modify the example.toml (of create your own) TOML configuration file to
point to your specific Oasis .csv files and you Oasis server. Then simply use
that config file as seen here:

```sh
$ cd path/to/spittalpond/
$ python ./spittalpond/config_interface.py ../examples/example.toml
```

Documentation on the config interface can be found [here].

Dependencies
------------

Core Spittalpond depends on the Python [Requests], and [pytoml] packages.
`pip install` this as necessary (if these dependencies are not automatically
resolved with the main setup command).

Also, of course, you will need to have [IPython] installed (as well as the
notebooks part of it) if you intend to view and run the IPython notebook
examples.

Contribute
----------

Additional features, patches, bug fixes, and pull request are welcome!
Please see the file [CONTRIBUTING.md]

Documentation
-------------

Documentation is available at
<http://beckettsimmons.github.io/spittalpond/docs/>

[here]: <http://beckettsimmons.github.io/spittalpond/docs/usage/config_interface.html>
[Requests]: <http://docs.python-requests.org/en/latest/>
[pytoml]: <https://github.com/avakar/pytoml>
[IPython]: <http://ipython.org/>
[CONTRIBUTING.md]: <./CONTRIBUTING.md>
