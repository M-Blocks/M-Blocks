(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
var World,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

World = (function() {
  function World() {
    this.render = __bind(this.render, this);
    this.animate = __bind(this.animate, this);
    this.onWindowResize = __bind(this.onWindowResize, this);
    this.init = __bind(this.init, this);
    this.camera = this.scene = this.renderer = this.mesh = this.controls = void 0;
    this.init();
    this.render();
  }

  World.prototype.init = function() {
    var directionalLight, geometry, helper, light, material;
    this.renderer = new THREE.WebGLRenderer({
      antialias: true
    });
    this.renderer.setClearColor(0xb0b0b0);
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement);
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
    this.camera.position.z = 500;
    this.scene.add(this.camera);
    this.controls = new THREE.OrbitControls(this.camera);
    this.controls.damping = 0.2;
    this.controls.addEventListener('change', this.render);
    geometry = new THREE.BoxGeometry(10, 10, 10);
    material = new THREE.MeshLambertMaterial({
      color: 0xb00000,
      wireframe: false
    });
    this.mesh = new THREE.Mesh(geometry, material);
    this.scene.add(this.mesh);
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

  return World;

})();

module.exports = new World();



},{}],2:[function(require,module,exports){
var world;

world = require('./World_Creator.coffee');



},{"./World_Creator.coffee":1}]},{},[2]);
