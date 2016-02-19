import itertools

from Queue import PriorityQueue
from MBlocks.reocnfig.configuration import Config

def find_closest(C1, C2):
	pass

def join(C1, C2):
	pass

def find_path(start, goal):
	pass

def bridge(start, goal, C1, C2):
	if not is_path(start, goal):
		join(start, goal, C1, C2)
	find_path(start, goal)