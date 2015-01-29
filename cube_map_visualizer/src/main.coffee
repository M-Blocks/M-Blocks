"use strict"

# Libraries
WebSocket = require 'ws'
Cube = require './Cube_Factory.coffee'
World = require './World_Creator.coffee'
u = require 'underscore'

class CubeManager

	constructor: () ->
		# This object keeps track of every cube that exists in our world
		@cubeDatabase = {}

		# Initialize the world
		@world = new World()

		# Connect to the visualizer supervisor as a client
		@ws = new WebSocket('ws://127.0.0.1:8080')
		@ws.onopen = () ->
			console.log 'Socket opened'

		@ws.onmessage = (message, flags) =>
			# New cube status update inbound. Handle it!
			payload = JSON.parse(message.data)
			@update_cube_status(payload)

		## Debugging functions
		# Make a unique cube
		# cube1 = new Cube {serialNumber:123}
		# @world.addObj cube1.Object3D

	update_cube_status: (cube_status) =>
		# Check if the cube is currently in our world
		cubeSerialNumber = cube_status.serialNumber
		cube = undefined

		if u.has( @cubeDatabase, cubeSerialNumber) # Then the object exists.
			cube = @cubeDatabase[cubeSerialNumber]
			# Reset the self-destruct timer
			cube.resetSelfDestructTimer()
		else
			# The cube does not exist, thus we must remake our cube model and its self destruct methods.
			cube = @makeNewCube(cube_status)

		# Add the cube to our inventory of cubes.
		@cubeDatabase[cubeSerialNumber] = cube

		# Add the cube to the world
		@world.addObj(cube.Object3D)

		# reconfigure placement of all cubes
		@rearrangeCubes()

	makeNewCube: (cube_status) =>
		cube = new Cube(cube_status)
		cube.on 'selfDestruct', () =>
			console.log "Self destruct initiated for #{cube.serialNumber}."
			@world.removeObj(cube.serialNumber)

		return cube

	rearrangeCubes: () =>



# Main program
cubeManager = new CubeManager()
