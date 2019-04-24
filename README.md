unikold.timeslots
=================

Dexterity based re-implementation of https://github.com/collective/uwosh.timeslot with extended functionalities.

Features
--------

- coming up


Installation
------------

Install unikold.timeslots by adding it to your buildout::

    [buildout]

    ...

    eggs =
        unikold.timeslots


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/unikold.timeslots/issues
- Source Code: https://github.com/collective/unikold.timeslots
- Documentation: https://docs.plone.org/foo/bar


Development
----------

Setup in project folder:

```
virtualenv --clear -p python2.7 venv
source venv/bin/activate
pip install -r requirements.txt
buildout bootstrap
bin/buildout -n -c buildout.cfg code-analysis:return-status-codes=True code-analysis:flake8-max-line-length=100
```

Run tests: `bin/test`

Run static code analysis (flake8): `bin/code-analysis`


License
-------

The project is licensed under the GPLv2.
