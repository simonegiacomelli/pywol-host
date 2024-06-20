import http
from typing import Dict, Type

import os
from functools import partial
from http.server import HTTPServer
import base64
import json
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse, parse_qs

print = partial(print, flush=True)


class RequestHandler(SimpleHTTPRequestHandler):
    auth_file = Path('.auth.txt')  # username:password see RFC 7617
    query_index = 4
    path_index = 2

    def __init__(self, *args
                 , handler: Callable[['RequestHandler'], bool]
                 , **kwargs):
        self.handler = handler
        super(RequestHandler, self).__init__(*args, **kwargs)

    def do_GET(self):
        if not self.authorized():
            self.send_string('not authorized', code=401)
            return
        if not self.handler(self):
            super(RequestHandler, self).do_GET()

    def decode_request(self):
        p = urlparse(self.path)
        query_str = p[self.query_index]
        rpath = p[self.path_index]
        di = parse_qs(query_str)
        params = {k: v[0] for k, v in di.items()}
        return params, rpath

    def authorized(self):
        if not self.auth_file.exists():
            return True
        auth_raw = self.headers.get('Authorization', '').split(' ')
        if len(auth_raw) != 2 or auth_raw[0] != 'Basic':
            return False
        auth_decoded = base64.b64decode(auth_raw[1]).decode('utf-8')
        return auth_decoded == self.auth_file.read_text()

    def send_json(self, obj):
        self.send_string(json.dumps(obj, indent=2), content_type='application/json')

    def send_string(self, message, code=200, content_type='text/plain'):
        self.protocol_version = "HTTP/1.1"
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(message)))
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("WWW-Authenticate", "Basic")
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))

    def serve_file(self, directory, filename):
        self.directory = directory
        self.path = '/' + filename
        super(RequestHandler, self).do_GET()


class ApiHandler:
    request: RequestHandler


def start(api_handler_class: Type[ApiHandler], port: int):
    script_dir = os.path.dirname(__file__)
    if script_dir != '':
        os.chdir(script_dir)
    print('Starting server web v0.1 on port %d...' % port)
    print(f'A possible address http://localhost:{port}')

    api_dispatch = Dispatch().register(api_handler_class, 'API_')

    def handler(request: RequestHandler) -> bool:
        params, rpath = request.decode_request()
        api_name = rpath[1:]  # remove initial /
        print('api_name = ' + api_name)
        if api_name == 'list':
            request.send_json(list(api_dispatch.registered.keys()))
        elif api_name == '':
            request.serve_file(script_dir, "index.html")
        elif api_name == 'favicon.ico':
            request.send_response(404, '')
        else:
            instance = api_handler_class()
            instance.request = request
            result = api_dispatch.dispatch(instance, api_name, params)
            if isinstance(result, str):
                print(result)
                request.send_string(result)
            elif isinstance(result, (list, set, dict, tuple)):
                request.send_json(result)
            else:
                request.send_json(result.__dict__)

        return True

    httpd = http.server.ThreadingHTTPServer(('', port), partial(RequestHandler, handler=handler))
    httpd.timeout = 10
    print('serving...')
    httpd.serve_forever()
    exit(0)


class Dispatch:
    def __init__(self, ):
        self.registered = {}
        self.prefix: str = None

    def register(self, clazz, prefix):
        self.registered = {d[len(prefix):]: getattr(clazz, d) for d in dir(clazz) if
                           d.startswith(prefix) and not d.startswith('__')}
        self.prefix = prefix
        return self

    def dispatch(self, instance, method_name, params: Dict = {}):
        if method_name not in self.registered.keys():
            raise MethodNotRegistered(method_name)
        m = getattr(instance, self.prefix + method_name)
        return m(**params)


class MethodNotRegistered(Exception):
    pass
