# How to test and what to do if things break.

Download [IPython](http://ipython.org/) and make sure you have pip.

Clone the Github repository from [https://github.com/sebastian-claici/M-Blocks](https://github.com/sebastian-claici/M-Blocks).

Open a terminal in the directory and run `pip install -r requirements.txt` to fetch all packages needed to run the code.

## Single Cube Light Tracking

There are two planners in MBlocks.planning. The first does lattice planning, so the cube needs to be placed on top of a lattice of other static cubes. This planner uses many plane change operations, so prepare to be annoyed when things randomly fail.

The other planner executes random moves when it does not find a good forward/reverse move. Unlike the previous planner, this has no stopping protocol. We could have used the same thresholding stopping condition, but I just want to see the cube vaguely moving towards the light source.

There is a file called `demo_utils.py` that helps with connections. My workflow looked something like this:

Open IPython and cd into M-Blocks. Run the following:

    from demo_utils import *
    cubes = find_cubes()

Create a planner and perform a few moves:

    planner = LatticeLightPlanner(cubes)
    moves = planner.next_moves()
    planner.execute_moves(moves)

If things broke, disconnect from everything:

    close_conns()

The two commands

    moves = planner.next_moves()
    planner.execute_moves(moves)

will run one iteration of the planner. Just use them again to do it all over. This is better than running it in a loop from my experience.

## Two Cube Light Tracking

Both cubes need to be able to read both the faceboard and central IMU with 100% accuracy for this to work. To start, just connect two cubes together and place them anywhere in the environment. Then run

	from MBlocks.control.controller import Cube
	from MBlocks.control.twocube import TwoCubeController

	fst = Cube('com3')
	scd = Cube('com4')
	control = TwoCubeController(fst, scd)

Then you can use `control.drive()` to do one step of the process (involving reorientation + two traverses).

## Failure

If the cubes fail, and you can't type into the IPython window anymore, open up a new IPython window, import `demo_utils` and run `close_conns()`.
