#!/bin/bash

# Build the visualizer code using browserify
browserify -t coffeeify src/main.coffee > dist/bundle.js

# Run the supervisor
coffee visualizer_supervisor.coffee