#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import json
import time

from test_base import ManageKVS


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.kvs = ManageKVS(8010, './test_kvs')

    def tearDown(self):
        self.kvs.stop_kvs()
        self.kvs.rm_storage()

    def test_start_stop_kvs(self):
        self.kvs.start_kvs()
        self.kvs.stop_kvs()

    def test_cache_kvs(self):
        self.kvs.start_kvs()

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

        self.kvs.stop_kvs()

        self.kvs.start_kvs()

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

        self.kvs.stop_kvs()

    def test_data_kvs(self):
        self.kvs.start_kvs()

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

        self.kvs.stop_kvs()


if __name__ == "__main__":
    unittest.main()
