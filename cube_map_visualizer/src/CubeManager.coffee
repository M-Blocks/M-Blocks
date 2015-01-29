Cube = require './Cube_Factory.coffee'

class CubeManager

	constructor: () ->
		# This object keeps track of every cube that exists in our world
		@cubeDatabase = {}

	update_cube_status: (cube_status) =>
		# Check if the cube is currently in our world
		cubeSerialNumber = cube_status.serialNumber

		if @cubeDatabase[cubeSerialNumber]?
			# Delete the existing cube
			delete @cubeDatabase[cubeSerialNumber]
		
		# make the missing cube with the current neighbor values
		@cubeDatabase[cubeSerialNumber] = cube_status

		@cubeDatabase[cubeSerialNumber].cube 

		# reconfigure placement of all cubes

module.exports = CubeManager