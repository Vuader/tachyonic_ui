=========
Tachyonic
=========

.. image:: https://travis-ci.org/TachyonProject/tachyonic_ui.svg?branch=master
    :target: https://travis-ci.org/TachyonProject/tachyonic_ui

Quick Links
-----------

* `Website <http://tachyonic.co.za>`__.
* `Documentation <http://tachyonic-ui.readthedocs.io>`__.

Installation
------------

Tachyon currently fully supports `CPython <https://www.python.org/downloads/>`__ 3.6.

Source Code
-----------

Tachyon UI infrastructure and code is hosted on `GitHub <https://github.com/TachyonProject/tachyonic_ui>`_.
Making the code easy to browse, download, fork, etc. Pull requests are always welcome!

Clone the project like this:

.. code:: bash

    $ git clone https://github.com/TachyonProject/tachyonic_ui.git

Once you have cloned the repo or downloaded a tarball from GitHub, you
can install Tachyon like this:

.. code:: bash

    $ cd tachyonic_ui
    $ pip install .

Or, if you want to edit the code, first fork the main repo, clone the fork
to your desktop, and then run the following to install it using symbolic
linking, so that when you change your code, the changes will be automagically
available to your app without having to reinstall the package:

.. code:: bash

    $ cd tachyonic_ui
    $ pip install -e .

You can manually test changes to the tachyonic_ui by switching to the
directory of the cloned repo:

.. code:: bash

    $ pip install -r requirements-dev.txt
    $ paver test
