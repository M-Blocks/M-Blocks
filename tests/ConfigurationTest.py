from nose.tools import *

from src.configuration import *

def set_up(self):
    self.config = Configuration([(0,0,0), (0,0,1), (0,1,0), (0,1,1),
                                 (1,0,0), (1,0,1), (1,1,0), (1,1,1)])

def test_neighbors(self):
    self.assertEqual(self.config._neighbors((0,0,0)),
                     [(0,0,1), (0,1,0), (1,0,0)])
