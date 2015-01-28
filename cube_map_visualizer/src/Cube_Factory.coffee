###
This file will make a cube representation of the M-Block objects in 3D space.

NOTE: This file will use global three.js functions that have been defined globally in the DOM 

Winter Guerra <winterg@mit.edu>, January 2015
###



class Cube

	# Class variables
	size = 10
	separation = size # Distance that all cubes should be from each other in XYZ
	faceTexture = undefined

	constructor: (@serialNumber, @orientation) ->

		# Instance variables
		@Object3D = new THREE.Object3D()

		@create3DFeatures()



		# Set self destruct timer to get rid of cube if it has not been poked in a few seconds.

	# Returns a group
	getObject3D: () ->




	create3DFeatures: () ->

		# Make 3D cube object
		geometry = new THREE.BoxGeometry(size, size, size)

		# Check if an object has already created a cached faceTexture map for the cube class
		if not faceTextures?
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
			# Save the texture in a class variable
			faceTexture = new THREE.MeshFaceMaterial(faceTextures) 
			
		# Load the texture from a class variable
		mesh = new THREE.Mesh( geometry, faceTexture )

		# Add the cube mesh to the 3D display group
		@Object3D.add mesh

		# Make serial number display
		console.log "Serial number: #{@serialNumber}"
		serialNumberSprite = @makeTextSprite "#{@serialNumber}"

		@Object3D.add serialNumberSprite



	makeTextSprite: (message, parameters) ->

		parameters = {}	if parameters is `undefined`
		fontface = "Arial"
		fontsize = 18
		borderThickness = 4
		borderColor = (if parameters.hasOwnProperty("borderColor") then parameters["borderColor"] else
			r: 0
			g: 0
			b: 0
			a: 1.0
		)
		backgroundColor = (if parameters.hasOwnProperty("backgroundColor") then parameters["backgroundColor"] else
			r: 255
			g: 255
			b: 255
			a: 1.0
		)
		
		
		canvas = document.createElement("canvas")
		context = canvas.getContext("2d")
		context.font = "Bold " + fontsize + "px " + fontface
		
		# get size data (height depends only on font size)
		metrics = context.measureText(message)
		textWidth = metrics.width
		
		# background color
		context.fillStyle = "rgba(" + backgroundColor.r + "," + backgroundColor.g + "," + backgroundColor.b + "," + backgroundColor.a + ")"
		
		# border color
		context.strokeStyle = "rgba(" + borderColor.r + "," + borderColor.g + "," + borderColor.b + "," + borderColor.a + ")"
		context.lineWidth = borderThickness
		@roundRect context, borderThickness / 2, borderThickness / 2, textWidth + borderThickness, fontsize * 1.4 + borderThickness, 6
		
		# 1.4 is extra height factor for text below baseline: g,j,p,q.
		
		# text color
		context.fillStyle = "rgba(0, 0, 0, 1.0)"
		context.fillText message, borderThickness, fontsize + borderThickness
		
		# canvas contents will be used for a texture
		texture = new THREE.Texture(canvas)
		texture.needsUpdate = true
		spriteMaterial = new THREE.SpriteMaterial(
			map: texture
		)
		sprite = new THREE.Sprite(spriteMaterial)
		sprite.scale.set 100, 50, 1.0
		return sprite

	# function for drawing rounded rectangles
	roundRect: (ctx, x, y, w, h, r) ->
		ctx.beginPath()
		ctx.moveTo x + r, y
		ctx.lineTo x + w - r, y
		ctx.quadraticCurveTo x + w, y, x + w, y + r
		ctx.lineTo x + w, y + h - r
		ctx.quadraticCurveTo x + w, y + h, x + w - r, y + h
		ctx.lineTo x + r, y + h
		ctx.quadraticCurveTo x, y + h, x, y + h - r
		ctx.lineTo x, y + r
		ctx.quadraticCurveTo x, y, x + r, y
		ctx.closePath()
		ctx.fill()
		ctx.stroke()
		return




module.exports = Cube



