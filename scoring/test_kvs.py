#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import subprocess
import signal
import unittest
import http.client
import json
import time


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.storage_path = pathlib.Path('./test_kvs')
        self.rm_storage()
        self.storage_path.mkdir(parents=True)
        self.port = 8080
        self.kvs = None

    def tearDown(self):
        if self.kvs is not None:
            self.stop_kvs()
        self.rm_storage()

    def rm_storage(self):
        if self.storage_path.is_dir():
            for path_file in self.storage_path.iterdir():
                path_file.unlink()
            self.storage_path.rmdir()

    def start_kvs(self):
        if self.kvs is not None:
            self.stop_kvs()
        self.kvs = subprocess.Popen(['./kvs.py', '-p', str(self.port), '-s', str(self.storage_path)])
        try_num = 0
        while (True):
            try_num += 1
            try:
                connect = http.client.HTTPConnection('localhost', self.port, 1)
                connect.request('GET', '/ping')
                response = connect.getresponse()
                return
            except ConnectionRefusedError as e:
                if try_num < 3:
                    time.sleep((try_num + 1) * 0.1)
                else:
                    raise

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
        connect.request('POST', path, request)
        return connect.getresponse()

    def test_cache_kvs(self):
        self.start_kvs()
        response = self.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertIsNone(response_decoded['response'])

        response = self.make_request('/cache_set', '{"key": "123", "value": { "a": 1, "b": 2 } }')
        self.assertEqual(response.status, 200)

        response = self.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertDictEqual(response_decoded['response'], {"a": 1, "b": 2})
        self.stop_kvs()

        self.start_kvs()
        response = self.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertIsNone(response_decoded['response'])

        response = self.make_request('/cache_set', '{"key": "123", "value": { "a": 1, "b": 2 }, "timeout": 0.5 }')
        self.assertEqual(response.status, 200)

        response = self.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertDictEqual(response_decoded['response'], {"a": 1, "b": 2})

        time.sleep(1)

        response = self.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertIsNone(response_decoded['response'])
        self.stop_kvs()

    def test_data_kvs(self):
        self.start_kvs()
        response = self.make_request('/data_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 422)
        self.assertEqual(response_decoded['code'], 422)

        response = self.make_request('/data_set', '{"key": "123", "value": { "a": 1, "b": 2 }, "timeout": 1 }')
        self.assertEqual(response.status, 200)

        response = self.make_request('/data_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertDictEqual(response_decoded['response'], {"a": 1, "b": 2})


if __name__ == "__main__":
    unittest.main()
