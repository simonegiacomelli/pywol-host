import os
from functools import partial
from http.server import HTTPServer

from dispatch import Dispatch
from api_server import ApiServer
from request_handler import RequestHandler


def start(api_handler_class):
    script_dir = os.path.dirname(__file__)
    if script_dir != '':
        os.chdir(script_dir)
    port = 8090
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

    httpd = HTTPServer(('', port), partial(RequestHandler, handler=handler))
    httpd.timeout = 10

    print('serving...')
    httpd.serve_forever()
    exit(0)
