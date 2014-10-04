.. M-Blocks documentation master file, created by
   sphinx-quickstart on Fri Oct  3 14:12:29 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to M-Blocks's documentation!
====================================

API
***

.. automodule:: controller
   :members:

Examples
********

I would recommend importing :mod:`itertools` as it makes things
easier.

A simple example is to make the cube move back and forward on a
lattice. We'll take a lattice of length 5. Here's the full code to
connect to the cube, setup the list of commands, and send the
commands::

    from itertools import chain, cycle, repeat
    from controller import *

    cube1 = connect('/dev/ttyACM0', 115200)

    # Repeat forward and backward 5 times
    forward = repeat('ia f 6000 2500 250', 5)
    backward = repeat('ia r 6000 2500 250', 5)

    # Combine the two in a cycle
    c = cycle(chain(forward, backward))

    # Send commands with 3s delay between consecutive commands
    command([cube1], c, repeat(3))


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

