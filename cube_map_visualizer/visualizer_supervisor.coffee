http = require("http")
send = require("send")
url = require("url")
app = http.createServer((req, res) ->
  send(req, url.parse(req.url).pathname).root(__dirname).pipe res
  return
)
app.listen 8337, "127.0.0.1"
console.log "Listening on http://127.0.0.1:8337/"
console.log "Load http://127.0.0.1:8337/visualizer/ for the demo."


# Open the visualizer in chrome
spawn = require("child_process").spawn
chrome = spawn("open", [
  "http://127.0.0.1:8337/visualizer/"
])
# ls.stdout.on "data", (data) ->
#   console.log "stdout: " + data
#   return

# ls.stderr.on "data", (data) ->
#   console.log "stderr: " + data
#   return

# ls.on "close", (code) ->
#   console.log "child process exited with code " + code
#   return
