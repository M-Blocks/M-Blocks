from nose.tools import *

from MBlocks.configuration import Config

def test_neighbors():
    config = Config([(0,0,0), (0,0,1), (0,1,0), (0,1,1),
                     (1,0,0), (1,0,1), (1,1,0), (1,1,1)])
    assert_equal(set(config._neighbors((0,0,0))),
                 set([(0,0,1), (0,1,0), (1,0,0)]))

def test_connected():
    config = Config([(0,0,0), (0,0,1), (0,1,0), (0,1,1),
                     (1,0,0), (1,0,1), (1,1,0), (1,1,1)])
    assert(config._is_connected())
