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
console.log "If you ran demo/build.sh, load http://127.0.0.1:8337/demo-build/ to run the built code"