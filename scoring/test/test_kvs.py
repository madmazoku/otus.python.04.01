#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import json
import time
import pathlib
import shutil

from test_base import ManageKVS


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path('./test_kvs')
        if self.root.is_dir():
            shutil.rmtree(str(self.root))
        self.root.mkdir(parents=True)
        self.kvs = ManageKVS(8010, self.root)

    def tearDown(self):
        self.kvs.stop()
        if self.root.is_dir():
            shutil.rmtree(str(self.root))

    def test_start_stop(self):
        self.kvs.start()
        self.kvs.stop()

    def test_cache_kvs(self):
        self.kvs.start()

        response = self.kvs.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertIsNone(response_decoded['response'])

        response = self.kvs.make_request('/cache_set', '{"key": "123", "value": { "a": 1, "b": 2 } }')
        self.assertEqual(response.status, 200)

        response = self.kvs.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertDictEqual(response_decoded['response'], {"a": 1, "b": 2})

        self.kvs.stop()

        self.kvs.start()

        response = self.kvs.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertIsNone(response_decoded['response'])

        response = self.kvs.make_request('/cache_set', '{"key": "123", "value": { "a": 1, "b": 2 }, "timeout": 0.5 }')
        self.assertEqual(response.status, 200)

        response = self.kvs.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertDictEqual(response_decoded['response'], {"a": 1, "b": 2})

        time.sleep(1)

        response = self.kvs.make_request('/cache_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertIsNone(response_decoded['response'])

        self.kvs.stop()

    def test_data_kvs(self):
        self.kvs.start()

        response = self.kvs.make_request('/data_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 422)
        self.assertEqual(response_decoded['code'], 422)

        response = self.kvs.make_request('/data_set', '{"key": "123", "value": { "a": 1, "b": 2 }, "timeout": 1 }')
        self.assertEqual(response.status, 200)

        response = self.kvs.make_request('/data_get', '{"key": "123"}')
        response_decoded = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response.status, 200)
        self.assertEqual(response_decoded['code'], 200)
        self.assertDictEqual(response_decoded['response'], {"a": 1, "b": 2})

        self.kvs.stop()
