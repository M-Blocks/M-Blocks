# A script that makes a cube using three.js

console.log "hello ."
THREE = require 'three'
console.log THREE

camera = scene = renderer = mesh = undefined


init = ->
	renderer = new THREE.WebGLRenderer()
	renderer.setSize window.innerWidth, window.innerHeight
	document.body.appendChild renderer.domElement
	
	#
	camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 1000)
	camera.position.z = 400
	scene = new THREE.Scene()
	geometry = new THREE.BoxGeometry(200, 200, 200)
	# texture = THREE.ImageUtils.loadTexture("textures/crate.gif")
	# texture.anisotropy = renderer.getMaxAnisotropy()
	# material = new THREE.MeshBasicMaterial(map: texture)

	# Temp texture
	material = new THREE.MeshLambertMaterial(
		color: 0xb00000
		wireframe: false
	)

	mesh = new THREE.Mesh(geometry, material)
	scene.add mesh

	light = new THREE.DirectionalLight( 0xffffff )
	light.position.set( 0, 0, 1 )
	scene.add( light )
	
	#
	window.addEventListener "resize", onWindowResize, false
	return 

onWindowResize = () ->
	camera.aspect = window.innerWidth / window.innerHeight
	camera.updateProjectionMatrix()
	renderer.setSize window.innerWidth, window.innerHeight
	return

animate = () ->
	requestAnimationFrame( () -> 
		console.log 
		animate() )
	mesh.rotation.x += 0.005
	mesh.rotation.y += 0.01
	renderer.render scene, camera
	return

init()
animate()
