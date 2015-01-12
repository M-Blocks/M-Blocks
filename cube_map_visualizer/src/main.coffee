# A script that makes a cube using three.js


# Initialize the world
world = require './World_Creator.coffee'

# Make the initial cube
initialCube = require './Cube_Factory.coffee'

world.addObj initialCube