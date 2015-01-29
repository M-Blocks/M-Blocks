###
This file will make a cube representation of the M-Block objects in 3D space.

NOTE: This file will use global three.js functions that have been defined globally in the DOM 

Winter Guerra <winterg@mit.edu>, January 2015
###

EventEmitter = require('events').EventEmitter

class Cube extends EventEmitter

	# Class variables
	size = 10
	separation = size # Distance that all cubes should be from each other in XYZ
	timeToLive = 5 # seconds

	constructor: (options) ->

		# Instance variables
		{@serialNumber, @orientation, @neighbors} = options
		@Object3D = new THREE.Object3D()
		@Object3D.name = @serialNumber
		@faceTexture = undefined
		@selfDestructTimer = undefined

		@create3DFeatures()

		# Set self destruct timer to get rid of cube if it has not been poked in a few seconds.
		@setSelfDestructTimer()

	setSelfDestructTimer: () =>
		@selfDestructTimer = setTimeout(self.selfDestruct, timeToLive*1000)

	resetSelfDestructTimer: () =>
		clearTimeout(@selfDestructTimer)

	selfDestruct: () =>
		@emit('selfDestruct')


	create3DFeatures: () ->

		# Make 3D cube object
		geometry = new THREE.BoxGeometry(size, size, size)

		
		# # Make a texture with the 3 digit serial number of the cube

		dynamicTexture = new THREEx.DynamicTexture(256, 256)
		dynamicTexture.context.font	= "bolder 128px Verdana";
		dynamicTexture.clear('blue')
		dynamicTexture.drawTextCooked "#{@serialNumber}", {
			fillStyle: 'red',
			align: 'center',
			lineHeight: 0.5

		}

		faceTextures = (new THREE.MeshBasicMaterial({map:dynamicTexture.texture}) for i in [0..6])
		# Save the texture in a class variable
		serialNumberTexture = new THREE.MeshFaceMaterial(faceTextures) 
			
		# Load the texture from a class variable
		mesh = new THREE.Mesh( geometry, serialNumberTexture )

		# Add the cube mesh to the 3D display group
		@Object3D.add mesh


	




module.exports = Cube



