WebSocketServer = require('ws').Server
express = require("express")
child_process = require "child_process"


app = express()

# Serve up static files
app.use(express.static(__dirname + '/'))
app.listen(8000)

# Start the websocket server
wss = new WebSocketServer({ port: 8080 })

# Tell the server how to broadcast messages to all clients
wss.broadcast = broadcast = (data) ->
	wss.clients.forEach each = (client) ->
		client.send(data)

# Tell the server how to handle incoming messages from the cubes
wss.on 'connection', connection = (ws) ->
	# Whenever there is a incoming message to the server, broadcast it to all visualizer clients
	ws.on 'message', incoming = (message) ->
		wss.broadcast(message)


console.log "Webserver on http://127.0.0.1:8000/"
console.log "Load http://127.0.0.1:8000/ for the demo."
console.log "Websocket server is online at ws://127.0.0.1:8080"


# Open the visualizer in chrome
chrome = child_process.spawn("open", [
  "http://127.0.0.1:8000/"
])
