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
			console.log 'Data socket to visualizer server opened'

		@ws.onmessage = (message, flags) =>
			# New cube status update inbound. Handle it!
			payload = JSON.parse(message.data)
			@update_cube_status(payload)

	getLocalTranslationForFace: (face) ->
		# Translation lookup table
		#console.log "Translating cube origin by ", Cube.size, "in #{face} direction"
		translationVec = @normal(face)
		translationVec.multiplyScalar(Cube.size)
		return translationVec
		

	normal: (axis) ->
		switch axis
			when 'x+'
				return new THREE.Vector3(1, 0, 0)
			when 'x-'
				return new THREE.Vector3(-1, 0, 0)
			when 'y+'
				return new THREE.Vector3(0, 1, 0)
			when 'y-'
				return new THREE.Vector3(0, -1, 0)
			when 'z+'
				return new THREE.Vector3(0, 0, 1)
			when 'z-'
				return new THREE.Vector3(0, 0, -1)
			else
				console.error "ERROR: unrecognized axis ", axis, " used for translation."
				return new THREE.Vector3(0, 0, 0)

	getRotationForFaceMate: (originFace, matedFace) ->
		# Check that our args are okay
		if not originFace? or not matedFace?
			console.error "Missing arguments to getRotationForFaceMate", originFace, matedFace
			return new THREE.Euler()

		originNormal = @normal(originFace)
		matedNormal = @normal(matedFace)
		# For manual checking of aligned and inverse cases
		negatedMatedNormal = new THREE.Vector3()
		negatedMatedNormal.copy(matedNormal).negate()

		rotationAxis = new THREE.Vector3()
		rotationEuler = new THREE.Euler()


		# Check to see if the normals are the same or inverses
		if originNormal.equals(matedNormal)
			# No rotation needed

		# Rotate the cube 180 if the opposite face needs to be mated
		else if originNormal.equals(negatedMatedNormal)
			rotationAxis.clone(originNormal).multiplyScalar(Math.PI)
			rotationEuler.setFromVector3(rotationAxis)

		else
		# normal(matedFace) x normal(origin face) will give an axis of rotation where a 90deg rotation will align the origin face to that of the mated face
			rotationAxis.crossVectors(originNormal, matedNormal).multiplyScalar(Math.PI/2)
			rotationEuler.setFromVector3(rotationAxis)

		return rotationEuler

	getGlobalPositionUsingRelativePositioning: (originVec, rotationEuler, localTranslationVec) ->
		# Rotate the translation vector so that the local translation is local to the origin cube
		newLocalTranslationVec = new THREE.Vector3()
		newLocalTranslationVec.copy(localTranslationVec)
		newLocalTranslationVec.applyEuler(rotationEuler)

		# Find the global translation vector
		globalTranslationVector = new THREE.Vector3()
		globalTranslationVector.addVectors(originVec, newLocalTranslationVec)
		return globalTranslationVector


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
			# Add the cube to the world
			@world.addObj(cube.Object3D)

		# Add the cube to our inventory of cubes.
		@cubeDatabase[cubeSerialNumber] = cube

		# reconfigure placement of all cubes
		@rearrangeCubes(@cubeDatabase)

		# Log the database
		#console.log 'Database: ', @cubeDatabase

	makeNewCube: (cube_status) =>
		cube = new Cube(cube_status)
		cube.on 'selfDestruct', () =>
			console.log "Self destruct initiated for #{cube.serialNumber}."
			@world.removeObj(cube.serialNumber)
			delete @cubeDatabase[cube.serialNumber]

		return cube

	getCube: (cubeSerialNumber) =>
		return @cubeDatabase[cubeSerialNumber]

	rearrangeCubes: (cubes, startingPosition = new THREE.Vector3()) =>
		# Let's grab the cube with the most neighbors. This will be our origin cube.
		originCube = @getCubeWithMostNeighbors(cubes)
		# Make sure that we have a valid starting point
		if originCube is null
			return
		# Place the origin cube
		originCube.Object3D.position.copy( startingPosition )

		# Now, find and place all of the origin cube's neighbors
		placedCubes = [originCube.serialNumber]
		cubesToTraverse = [originCube.serialNumber]
		
		# traverse the cube block
		while cubesToTraverse.length > 0
			centerCube = @getCube(cubesToTraverse.pop())
			# Get the cube's neighbors
			neighbors = @getCubeNeighbors(centerCube)

			for {cubeObj, localFace, serialNumber, orientation} in neighbors
				# Place the origin cube's neighbors

				# Check that we have not placed this cube before
				if serialNumber in placedCubes
					# Skip this iteration of the loop
					continue

				# Find the local translation vector of the cube about to be placed
				localTranslation = @getLocalTranslationForFace(localFace)
				# Find the global position of the new cube
				globalPosition = @getGlobalPositionUsingRelativePositioning(centerCube.Object3D.position, centerCube.Object3D.rotation, localTranslation)

				# Set the new global position of the cube
				@world.positionObj(serialNumber, globalPosition)

				# Now, save this cube's serial number so that we do not try to place it again.
				placedCubes.push(serialNumber)
				# We should traverse this cube's neighbors sometime in the future
				cubesToTraverse.push(serialNumber)

				# Now, find the rotation needed on the neighboring cube for mating the two faces
				matedFace = @getMatedFace(centerCube.serialNumber, serialNumber)
				matingRotation = @getRotationForFaceMate(localFace, matedFace)
				# Rotate the neighboring cube to mate the correct faces
				@world.rotateObj(serialNumber, matingRotation)


				#console.log "Placing neighbor #{serialNumber} next to #{originCube.serialNumber} at pos", globalPosition 

	getMatedFace: (originSerialNumber, matedSerialNumber) =>
		matedCube = @getCube(matedSerialNumber)

		# Look for the origin serial number in matedCube.neighbors
		neighbors = @getCubeNeighbors(matedCube)
		for {cubeObj, localFace, serialNumber, orientation} in neighbors
			if serialNumber is originSerialNumber
				return localFace
		# If we get here, then the mated cube has failed to tell the visualizer that it is mated to another cube
		console.error "ERROR: cube #{originSerialNumber} says that it is mated to #{matedSerialNumber}. However, cube #{matedSerialNumber} does not report that it is mated to #{originSerialNumber}. Please check #{matedSerialNumber} for bugs."
		return null

		
	getCubeNeighbors: (startingCube) =>
		# Get the cube's neighbors and the faces that they are attached to
		neighbors = []
		for localFace, neighborObj of startingCube.neighbors
			# If there is a neighboring cube at this face, place the cube
			if neighborObj?
				neighbor = 
					'localFace': localFace
					'cubeObj': @cubeDatabase[neighborObj.serialNumber]
					'serialNumber': neighborObj.serialNumber
					'orientation': neighborObj.orientation

				# Check that the neighboring cube exists in our world before pushing
				if neighbor.cubeObj?
					neighbors.push(neighbor)

		#console.log "Neighbors of #{startingCube.serialNumber}: ", neighbors
		return neighbors

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
