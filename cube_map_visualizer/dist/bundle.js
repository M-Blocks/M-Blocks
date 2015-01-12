(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){

/*
This file will make a cube representation of the M-Block objects in 3D space.

NOTE: This file will use global three.js functions that have been defined globally in the DOM 

Winter Guerra <winterg@mit.edu>, January 2015
 */
var Cube,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

Cube = (function() {
  var separation, size;

  size = 10;

  separation = size;

  function Cube(options) {
    this.options = options;
    this.create3DFeatures = __bind(this.create3DFeatures, this);
    this.mesh = void 0;
    this.create3DFeatures();
  }

  Cube.prototype.create3DFeatures = function() {
    var faceNum, faceTextures, geometry, _fn, _i;
    geometry = new THREE.BoxGeometry(size, size, size);
    faceTextures = [];
    _fn = function(faceNum) {
      var dynamicTexture;
      dynamicTexture = new THREEx.DynamicTexture(256, 256);
      dynamicTexture.context.font = "bolder 128px Verdana";
      dynamicTexture.clear('blue');
      dynamicTexture.drawText("" + faceNum, void 0, 192, 'red');
      return faceTextures.push(new THREE.MeshBasicMaterial({
        map: dynamicTexture.texture
      }));
    };
    for (faceNum = _i = 1; _i <= 6; faceNum = ++_i) {
      _fn(faceNum);
    }
    return this.mesh = new THREE.Mesh(geometry, new THREE.MeshFaceMaterial(faceTextures));
  };

  return Cube;

})();

module.exports = new Cube();



},{}],2:[function(require,module,exports){

/*
This file makes the background for the 3d render

NOTE: This file will use global three.js functions that have been defined globally in the DOM 

Winter Guerra <winterg@mit.edu>, January 2015
 */
var World,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

World = (function() {
  function World() {
    this.addObj = __bind(this.addObj, this);
    this.render = __bind(this.render, this);
    this.animate = __bind(this.animate, this);
    this.onWindowResize = __bind(this.onWindowResize, this);
    this.init = __bind(this.init, this);
    this.camera = this.scene = this.renderer = this.controls = void 0;
    this.init();
    this.render();
  }

  World.prototype.init = function() {
    var directionalLight, helper, light;
    this.renderer = new THREE.WebGLRenderer({
      antialias: true
    });
    this.renderer.setClearColor(0xb0b0b0);
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement);
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
    this.camera.position.z = 500;
    this.camera.lookAt(new THREE.Vector3());
    this.scene.add(this.camera);
    this.controls = new THREE.OrbitControls(this.camera);
    this.controls.damping = 0.2;
    this.controls.addEventListener('change', this.render);
    light = new THREE.AmbientLight(0x222222);
    this.scene.add(light);
    directionalLight = new THREE.DirectionalLight(0xffffff);
    directionalLight.position.set(1, 0.75, 1).normalize();
    this.scene.add(directionalLight);
    helper = new THREE.GridHelper(80, 10);
    helper.rotation.x = Math.PI / 2;
    this.scene.add(helper);
    window.addEventListener("resize", this.onWindowResize, false);
    return this.animate();
  };

  World.prototype.onWindowResize = function() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    return this.render();
  };

  World.prototype.animate = function() {
    requestAnimationFrame(this.animate);
    return this.controls.update();
  };

  World.prototype.render = function() {
    return this.renderer.render(this.scene, this.camera);
  };

  World.prototype.addObj = function(object, position) {
    var mesh;
    mesh = object.mesh;
    if (position != null) {
      mesh.position.set(position);
    }
    this.scene.add(mesh);
    return this.render();
  };

  return World;

})();

module.exports = new World();



},{}],3:[function(require,module,exports){
var initialCube, world;

world = require('./World_Creator.coffee');

initialCube = require('./Cube_Factory.coffee');

world.addObj(initialCube);



},{"./Cube_Factory.coffee":1,"./World_Creator.coffee":2}]},{},[3]);
