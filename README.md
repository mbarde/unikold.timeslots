
unikold.timeslots
=================

Dexterity based re-implementation of https://github.com/collective/uwosh.timeslot with extended functionalities.
> uwosh.timeslot offers a simple way to allow users of a Plone site to
register for events (for example: training sessions or office hours).

Originally this was an extension of `uwosh.timeslot` for usage in the CMS of the [University of Koblenz -Landau]([http://uni-koblenz-landau.de](http://uni-koblenz-landau.de/)).

Features
--------

- Define date based timeslots users can sign up to
- Logged in users can watch and manage their signups
- Timeslots can have capacities (waiting list and automatically moving up included)
- Customizable notification emails
- Dynamically extend signup form with EasyForm ([https://github.com/collective/collective.easyform](https://github.com/collective/collective.easyform))

User states:
1. `unconfirmed`: Manager hast to confirm signup
2. `signedup`: User is signed up
3. `signedoff`: User is not signed up
4. `waiting`: User is on waiting list (moves up when another signup is cancelled)


Dependecies
--------

* [https://github.com/collective/collective.easyform](https://github.com/collective/collective.easyform)


Installation
------------

Install unikold.timeslots by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.easyform
        unikold.timeslots


and then running ``bin/buildout``.


Usage
------------

1. Create `UTSignupSheet`
2. Add `UTDay`
3. Add `UTTimeslot`

Optional: Create `EasyForm` and set as additional form in `UTSignupSheet` settings

**Important**: Ensure MailHost is configured properly (https://docs.plone.org/adapt-and-extend/config/mail.html).

Contribute
----------

- Issue Tracker: https://github.com/collective/unikold.timeslots/issues
- Source Code: https://github.com/collective/unikold.timeslots


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
