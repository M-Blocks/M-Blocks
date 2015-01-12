#!/bin/bash

# Build the visualizer code using browserify
browserify -t coffeeify src/cube_renderer.coffee > dist/bundle.js

# Run the supervisor
coffee visualizer_supervisor.coffee