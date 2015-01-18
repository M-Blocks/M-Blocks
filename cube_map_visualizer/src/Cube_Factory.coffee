###
This file will make a cube representation of the M-Block objects in 3D space.

NOTE: This file will use global three.js functions that have been defined globally in the DOM 

Winter Guerra <winterg@mit.edu>, January 2015
###



class Cube

	# Class variables
	size = 10
	separation = size # Distance that all cubes should be from each other in XYZ

	constructor: (@options) ->

		# Instance variables
		@mesh = undefined

		@create3DFeatures()

		# Set self destruct timer to get rid of cube if it has not been poked in a few seconds.

	create3DFeatures: () ->

		# Make 3D cube object
		geometry = new THREE.BoxGeometry(size, size, size)
		
		# # Make 6 face textures with text from 1-6 
		faceTextures = []

		for faceNum in [1..6]
			do (faceNum) ->
				dynamicTexture = new THREEx.DynamicTexture(256, 256)
				dynamicTexture.context.font	= "bolder 128px Verdana";
				dynamicTexture.clear('blue')
				dynamicTexture.drawTextCooked "#{faceNum}", {
					fillStyle: 'red',
					align: 'center',
					lineHeight: 0.5

				}
				faceTextures.push( new THREE.MeshBasicMaterial {map:dynamicTexture.texture})

		# console.log faces

		# dynamicTexture = new THREEx.DynamicTexture(256, 256)
		# dynamicTexture.context.font	= "bolder 128px Verdana";
		# dynamicTexture.clear('white')
		# dynamicTexture.drawText "1", undefined, 192, 'red'

		@mesh = new THREE.Mesh( geometry, new THREE.MeshFaceMaterial(faceTextures) )


module.exports = new Cube()



