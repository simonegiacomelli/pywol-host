import http.server
import threading

port = 8090


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'ok')


def start_server():
    print('Starting server web v0.1 on port %d...' % port)
    print(f'Possibly http://127.0.0.1:{port}')
    print(f'Possibly http://0.0.0.0:{port}')
    server = http.server.ThreadingHTTPServer(('', port), Handler)
    server.serve_forever()


server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Server stopped")
