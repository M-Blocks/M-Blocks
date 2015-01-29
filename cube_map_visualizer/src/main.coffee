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

	update_cube_status: (cube_status) =>
		# Check if the cube is currently in our world
		cubeSerialNumber = cube_status.serialNumber
		cube = null

		if u.has( @cubeDatabase, cubeSerialNumber) # Then the object exists.
			cube = @cubeDatabase[cubeSerialNumber]
			# Reset the self-destruct timer
			cube.resetSelfDestructTimer()
			# Update neighbors and orientation
			cube.neighbors = cube_status.neighbors
			cube.orientation = cube_status.orientation
		else
			# The cube does not exist, thus we must remake our cube model and its self destruct methods.
			cube = @makeNewCube(cube_status)

		# Add the cube to our inventory of cubes.
		@cubeDatabase[cubeSerialNumber] = cube

		# Add the cube to the world
		@world.addObj(cube.Object3D)

		# reconfigure placement of all cubes
		@rearrangeCubes(@cubeDatabase)

	makeNewCube: (cube_status) =>
		cube = new Cube(cube_status)
		cube.on 'selfDestruct', () =>
			console.log "Self destruct initiated for #{cube.serialNumber}."
			@world.removeObj(cube.serialNumber)
			delete @cubeDatabase[cube.serialNumber]

		return cube

	rearrangeCubes: (cubes, startingPosition = [0,0,0]) =>
		# Let's grab the cube with the most neighbors. This will be our origin cube.
		originCube = @getCubeWithMostNeighbors(cubes)
		# Make sure that we have a valid starting point
		if originCube is null
			return
		# Place the origin cube
		originCube.Object3D.position.set( new THREE.Vector3(startingPosition) )

		# Now, find and place all of the origin cube's neighbors
		centerPosition = originCube.Object3D.position

		

		
		# Debug
		#console.log "Origin cube: ", originCube

	getCubeWithMostNeighbors: (cubes) =>
		originCube = 
			serialNumber: null
			connections: -1

		for serialNumber, cube of cubes
			# Count the connections
			connections = 0
			for face, neighborObj of cube.neighbors
				if neighborObj
					connections = connections + 1

			# Now, check to see if this is the most connected cube
			if connections > originCube.connections
				originCube.serialNumber = serialNumber
				originCube.connections = connections

		returnObj = if originCube.serialNumber isnt null then @cubeDatabase[originCube.serialNumber] else null
		return returnObj


# Main program
cubeManager = new CubeManager()
