# How to test and what to do if things break.

Hi,

We're going to be running experiments all through the next week. I'll be around for most of them, but in case I'm not there, here's what I want:

## Single Cube Light Tracking

We need to make sure that light tracking works for one cube. There are two planners in MBlocks.planning. The first does lattice planning, so the cube needs to be placed on top of a lattice of other static cubes. This planner uses many plane change operation, so prepare to be annoyed when things randomly fail.

The other planner executes random moves when it does not find a good forward/reverse move. Unlike the previous planner, this has no stopping protocol. We could have used the same thresholding stopping condition, but I just want to see the cube vaguely moving towards the light source.

Either of these planners can be run like this:

    from MBlocks.control.controller import Cube
	from MBlocks.planning.planner import LatticeLightPlanner
	
    cube = Cube('com3')
	planner = LatticeLightPlanner([cube]) # or RandomLightPlanner([cube])
	while True:
		moves = planner.next_moves()
		planner.execute_moves(moves)

You can run these with more than one cube (just pass a list of all cubes), but we won't have neighbor detection, so expect poor performance.

## Two Cube Light Tracking

Both cubes need to be able to read both the faceboard and central IMU with 100% accuracy for this to work. To start, just connect two cubes together and place them anywhere in the environment. Then run

	from MBlocks.control.controller import Cube
	from MBlocks.control.twocube import TwoCubeController

	fst = Cube('com3')
	scd = Cube('com4')
	control = TwoCubeController(fst, scd)
	while True:
		control.drive()

## Failure

If things fail (and I expect they will several times), I want to have all the information. Screenshot the terminal, write print statements to output information (e.g. print out `moves`), or just describe what happened. The code is in a good place, but since testing involves running it on the cubes, and the cubes themselves are fickle beings, I expect bugs to still be lurking.

I've committed the most up-to-date version to github on branch master.
