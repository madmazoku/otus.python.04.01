#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime
import logging
import hashlib
import uuid
import pathlib
import base64
import time
import collections
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}

CacheRecord = collections.namedtuple('CacheRecord', 'value expire')

cache = {}


def cache_get(request, headers, context):
    if 'key' not in request:
        return 'key not found', INVALID_REQUEST
    key = request['key']
    if key is None:
        return 'key is empty', INVALID_REQUEST
    value = None

    if key in cache:
        record = cache[key]
        if record.expire is None or record.expire >= time.time():
            value = record.value
        else:
            del cache[key]

    return value, OK


def cache_set(request, headers, context):
    if 'key' not in request:
        return 'key not found', INVALID_REQUEST
    key = request['key']
    if key is None:
        return 'key is empty', INVALID_REQUEST
    if 'value' not in request:
        return 'value not found', INVALID_REQUEST

    value = request.get('value', None)
    timeout = request.get('timeout', None)
    cache[request['key']] = CacheRecord(value, None if timeout is None else time.time() + timeout)

    return None, OK


def data_get(request, headers, context):
    if 'key' not in request:
        return 'key not found', INVALID_REQUEST
    key = request['key']
    if key is None:
        return 'key is empty', INVALID_REQUEST
    value = None

    key = base64.b64encode(request['key'].encode('utf-8')).decode('utf-8')
    path_rec = pathlib.Path(opts.storage) / (key + '.rec')
    if not path_rec.is_file():
        return 'no data found', INVALID_REQUEST
    value = json.loads(path_rec.read_text())

    return value, OK


def data_set(request, headers, context):
    if 'key' not in request:
        return 'key not found', INVALID_REQUEST
    key = request['key']
    if key is None:
        return 'key is empty', INVALID_REQUEST
    if 'value' not in request:
        return 'value not found', INVALID_REQUEST

    key = base64.b64encode(request['key'].encode('utf-8')).decode('utf-8')
    path_rec = pathlib.Path(opts.storage) / (key + '.rec')
    path_rec_tmp = path_rec.with_suffix('{:s}.{:s}.tmp'.format(path_rec.suffix, context['request_id']))
    try:
        path_rec_tmp.write_text(json.dumps(request['value']))
        path_rec_tmp.rename(path_rec)
    finally:
        if path_rec_tmp.is_file():
            path_rec_tmp.unlink()

    return None, OK


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"cache_get": cache_get, "cache_set": cache_set, "data_get": data_get, "data_set": data_set}

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_GET(self):
        code = NOT_FOUND
        context = {"request_id": self.get_request_id(self.headers)}

        path = self.path.strip("/")
        if path == 'ping':
            code = OK

        self.make_response(None, code, context)
        return

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        data_string = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string.decode("utf-8"))
        except Exception as e:
            logging.exception(e)
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](request, self.headers, context)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.make_response(response, code, context)
        return

    def make_response(self, response, code, context):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode("utf-8"))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("-s", "--storage", action="store", default='.')
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
