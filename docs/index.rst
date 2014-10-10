M-Blocks Scripts
====================================

API
***

.. automodule:: controller
   :members:

.. autoclass:: Cube
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

