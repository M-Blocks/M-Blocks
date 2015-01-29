###
This file makes the background for the 3d render

NOTE: This file will use global three.js functions that have been defined globally in the DOM 

Winter Guerra <winterg@mit.edu>, January 2015
###

"use strict"

class World

	constructor: () ->

		@camera = @scene = @renderer = @controls = undefined

		@init()
		@render()


	init : () =>

		# Make renderer
		@renderer = new THREE.WebGLRenderer( { antialias: true })
		@renderer.setClearColor( 0xb0b0b0 );
		@renderer.setSize window.innerWidth, window.innerHeight
		document.body.appendChild @renderer.domElement

		# Make scene
		@scene = new THREE.Scene()
		
		# Make Camera
		@camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000)
		@camera.position.z = 500
		@camera.lookAt( new THREE.Vector3() )
		@scene.add(@camera)
		

		# Make mouse-based controls
		@controls = new THREE.OrbitControls( @camera)
		@controls.damping = 0.2
		@controls.addEventListener( 'change', @render )

		# Make lights

		light = new THREE.AmbientLight( 0x222222 );
		@scene.add( light );

		directionalLight = new THREE.DirectionalLight( 0xffffff )
		directionalLight.position.set( 1, 0.75, 1 ).normalize()
		@scene.add( directionalLight )

		# Make XY grid
		helper = new THREE.GridHelper( 80, 10 )
		helper.rotation.x = Math.PI / 2
		@scene.add( helper )
		
		window.addEventListener "resize", @onWindowResize, false

		@animate()

	onWindowResize: () =>
		@camera.aspect = window.innerWidth / window.innerHeight
		@camera.updateProjectionMatrix()
		@renderer.setSize window.innerWidth, window.innerHeight
		@render()

	# Changes internal scenery, but does not redraw the page. That is now the job of the controller object
	animate: () =>
		requestAnimationFrame(@animate)
		@controls.update()

	# Repaint the 3D scene
	render: () =>
		@renderer.render @scene, @camera

	# Helper object for adding a mesh or object to the world
	addObj: (object, position) =>

		if position?
			object.position.set(position)

		@scene.add(object)

		# refresh the scene
		@render()

	removeObj: (objectName) =>
		object = @scene.getObjectByName(objectName)
		@scene.remove(object)

		@render()

	positionObj: (objectName, position) =>
		object = @scene.getObjectByName(objectName)
		object.position.set(position)




module.exports = World



