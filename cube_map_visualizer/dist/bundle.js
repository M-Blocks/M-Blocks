(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){

/*
This file will make a cube representation of the M-Block objects in 3D space.

NOTE: This file will use global three.js functions that have been defined globally in the DOM 

Winter Guerra <winterg@mit.edu>, January 2015
 */
var Cube;

Cube = (function() {
  var faceTexture, separation, size;

  size = 10;

  separation = size;

  faceTexture = void 0;

  function Cube(serialNumber, orientation) {
    this.serialNumber = serialNumber;
    this.orientation = orientation;
    this.Object3D = new THREE.Object3D();
    this.create3DFeatures();
  }

  Cube.prototype.getObject3D = function() {};

  Cube.prototype.create3DFeatures = function() {
    var faceNum, faceTextures, geometry, mesh, serialNumberSprite, _fn, _i;
    geometry = new THREE.BoxGeometry(size, size, size);
    if (typeof faceTextures === "undefined" || faceTextures === null) {
      faceTextures = [];
      _fn = function(faceNum) {
        var dynamicTexture;
        dynamicTexture = new THREEx.DynamicTexture(256, 256);
        dynamicTexture.context.font = "bolder 128px Verdana";
        dynamicTexture.clear('blue');
        dynamicTexture.drawTextCooked("" + faceNum, {
          fillStyle: 'red',
          align: 'center',
          lineHeight: 0.5
        });
        return faceTextures.push(new THREE.MeshBasicMaterial({
          map: dynamicTexture.texture
        }));
      };
      for (faceNum = _i = 1; _i <= 6; faceNum = ++_i) {
        _fn(faceNum);
      }
      faceTexture = new THREE.MeshFaceMaterial(faceTextures);
    }
    mesh = new THREE.Mesh(geometry, faceTexture);
    this.Object3D.add(mesh);
    console.log("Serial number: " + this.serialNumber);
    serialNumberSprite = this.makeTextSprite("" + this.serialNumber);
    return this.Object3D.add(serialNumberSprite);
  };

  Cube.prototype.makeTextSprite = function(message, parameters) {
    var backgroundColor, borderColor, borderThickness, canvas, context, fontface, fontsize, metrics, sprite, spriteMaterial, textWidth, texture;
    if (parameters === undefined) {
      parameters = {};
    }
    fontface = "Arial";
    fontsize = 18;
    borderThickness = 4;
    borderColor = (parameters.hasOwnProperty("borderColor") ? parameters["borderColor"] : {
      r: 0,
      g: 0,
      b: 0,
      a: 1.0
    });
    backgroundColor = (parameters.hasOwnProperty("backgroundColor") ? parameters["backgroundColor"] : {
      r: 255,
      g: 255,
      b: 255,
      a: 1.0
    });
    canvas = document.createElement("canvas");
    context = canvas.getContext("2d");
    context.font = "Bold " + fontsize + "px " + fontface;
    metrics = context.measureText(message);
    textWidth = metrics.width;
    context.fillStyle = "rgba(" + backgroundColor.r + "," + backgroundColor.g + "," + backgroundColor.b + "," + backgroundColor.a + ")";
    context.strokeStyle = "rgba(" + borderColor.r + "," + borderColor.g + "," + borderColor.b + "," + borderColor.a + ")";
    context.lineWidth = borderThickness;
    this.roundRect(context, borderThickness / 2, borderThickness / 2, textWidth + borderThickness, fontsize * 1.4 + borderThickness, 6);
    context.fillStyle = "rgba(0, 0, 0, 1.0)";
    context.fillText(message, borderThickness, fontsize + borderThickness);
    texture = new THREE.Texture(canvas);
    texture.needsUpdate = true;
    spriteMaterial = new THREE.SpriteMaterial({
      map: texture
    });
    sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(100, 50, 1.0);
    return sprite;
  };

  Cube.prototype.roundRect = function(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
  };

  return Cube;

})();

module.exports = Cube;



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
    if (position != null) {
      object.position.set(position);
    }
    this.scene.add(object);
    return this.render();
  };

  return World;

})();

module.exports = new World();



},{}],3:[function(require,module,exports){
var Cube, cube1, world;

world = require('./World_Creator.coffee');

Cube = require('./Cube_Factory.coffee');

cube1 = new Cube(1234);

world.addObj(cube1.Object3D);



},{"./Cube_Factory.coffee":1,"./World_Creator.coffee":2}]},{},[3]);
