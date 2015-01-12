# This file makes the background for the 3d render

# Import a patched version of three.js that includes orbit controls
#THREE = require './threejs_patched.coffee'


class World

	constructor: () ->

		@camera = @scene = @renderer = @mesh = @controls = undefined

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
		# @camera.position.set (0,0,30)
		@camera.position.z = 500
		#@camera.lookAt( new THREE.Vector3() )
		@scene.add(@camera)
		

		# Make mouse-based controls
		@controls = new THREE.OrbitControls( @camera)
		@controls.damping = 0.2
		@controls.addEventListener( 'change', @render )

		# Make test cube
		geometry = new THREE.BoxGeometry(10, 10, 10)
		# texture = THREE.ImageUtils.loadTexture("textures/crate.gif")
		# texture.anisotropy = renderer.getMaxAnisotropy()
		# material = new THREE.MeshBasicMaterial(map: texture)

		# Temp texture
		material = new THREE.MeshLambertMaterial(
			color: 0xb00000
			wireframe: false
		)

		@mesh = new THREE.Mesh(geometry, material)
		@scene.add @mesh

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

module.exports = new World()



