#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools

import pathlib
import subprocess
import signal
import http.client
import time
import json
import unittest


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c, ))
                if isinstance(args[0], unittest.TestCase):
                    with args[0].subTest(c):
                        f(*new_args)
                else:
                    f(*new_args)

        return wrapper

    return decorator


class ManageService(object):
    def __init__(self, port, command):
        self.port = port
        self.command = command
        self.process = None

    def start(self):
        if self.process is not None:
            self.stop()
        self.process = subprocess.Popen(self.command.split(' '))
        try_num = 0
        while True:
            try_num += 1
            connect = http.client.HTTPConnection('localhost', self.port, 1)
            try:
                connect.request('GET', '/ping', headers={'connection': 'close'})
                response = connect.getresponse()
                if response.status == 200:
                    response_decoded = json.loads(response.read().decode('utf-8'))
                    if response_decoded.get('code', None) == 200:
                        return
            except ConnectionError as e:
                if try_num < 3:
                    time.sleep(try_num * 0.1)
                else:
                    raise
            finally:
                connect.close()

    def stop(self):
        if self.process is None:
            return
        time.sleep(0.1)
        self.process.send_signal(signal.SIGINT)
        time.sleep(0.1)
        try:
            if not self.process.poll():
                self.process.wait(1)
        except subprocess.TimeoutExpired as e:
            self.process.terminate()
        self.process = None

    def restart(self):
        self.stop()
        self.start()

    def make_request(self, path, request):
        connect = http.client.HTTPConnection('localhost', self.port, 1)
        try:
            connect.request('POST', path, request)
            response = connect.getresponse()
        finally:
            connect.close()
        return response


class ManageKVS(ManageService):
    def __init__(self, port, root):
        super().__init__(port, "./kvs.py -p {:d} -s {!s} -l {!s}".format(port, root, root / 'report_kvs.log'))


class ManageAPI(ManageService):
    def __init__(self, port, root, storage_cfg):
        super().__init__(port, "./api.py -p {:d} -s {:s} -l {!s}".format(port, storage_cfg, root / 'report_api.log'))
