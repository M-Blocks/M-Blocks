# A script that makes a cube using three.js


# Initialize the world
world = require './World_Creator.coffee'

# Make cube class
Cube = require './Cube_Factory.coffee'

# Make a unique cube
cube1 = new Cube 1234


world.addObj cube1.Object3D
