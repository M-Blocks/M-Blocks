WebSocket = require('ws')
express = require("express")
child_process = require "child_process"


app = express()

# Serve up static files
app.use(express.static(__dirname + '/'))

app.listen(8000)


console.log "Listening on http://127.0.0.1:8000/"
console.log "Load http://127.0.0.1:8000/ for the demo."


# Open the visualizer in chrome

chrome = child_process.spawn("open", [
  "http://127.0.0.1:8000/"
])
