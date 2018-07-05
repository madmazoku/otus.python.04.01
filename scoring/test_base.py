#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools

import pathlib
import subprocess
import signal
import http.client
import time


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c, ))
                f(*new_args)

        return wrapper

    return decorator


class ManageKVS(object):
    def __init__(self, port, storage):
        self.kvs = None
        self.storage_path = pathlib.Path(storage)
        self.rm_storage()
        self.storage_path.mkdir(parents=True)
        self.port = port

    def rm_storage(self):
        if self.storage_path.is_dir():
            for path_file in self.storage_path.iterdir():
                path_file.unlink()
            self.storage_path.rmdir()

    def start_kvs(self):
        if self.kvs is not None:
            self.stop_kvs()
        self.kvs = subprocess.Popen([
            './kvs.py', '-p',
            str(self.port), '-s',
            str(self.storage_path), '-l',
            str(self.storage_path / 'report.log')
        ])
        try_num = 0
        while (True):
            try_num += 1
            connect = http.client.HTTPConnection('localhost', self.port, 1)
            try:
                connect.request('GET', '/ping', headers={'connection': 'close'})
                response = connect.getresponse()
                response.close()
                return
            except ConnectionError as e:
                if try_num < 3:
                    time.sleep((try_num + 1) * 0.1)
                else:
                    raise
            finally:
                connect.close()

    def stop_kvs(self):
        if self.kvs is None:
            return
        self.kvs.send_signal(signal.SIGINT)
        try:
            if not self.kvs.poll():
                self.kvs.wait(1)
        except subprocess.TimeoutExpired as e:
            self.kvs.terminate
        self.kvs = None

    def make_request(self, path, request):
        connect = http.client.HTTPConnection('localhost', self.port, 1)
        try:
            connect.request('POST', path, request)
            response = connect.getresponse()
        finally:
            connect.close()
        return response
