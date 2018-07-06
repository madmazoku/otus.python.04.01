#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import pathlib
import shutil
import json

import store
import test_api
from test_base import cases, ManageKVS, ManageAPI


class TestSuite(test_api.TestSuite, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = pathlib.Path('./test_api_integration')
        if cls.root.is_dir():
            shutil.rmtree(cls.root)
        cls.root.mkdir(parents=True)
        cls.kvs = ManageKVS(8012, cls.root)
        cls.api = ManageAPI(8082, cls.root, 'localhost,8012,10,3')
        cls.kvs.start()
        cls.api.start()
        cls.store = store.StoreKVS('localhost', 8012, 10, 3)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.api.stop()
        cls.kvs.stop()
        if cls.root.is_dir():
            shutil.rmtree(cls.root)

    def get_response(self, request):
        response = self.api.make_request('/method', json.dumps(request))
        response_decoded = json.loads(response.read().decode('utf-8'))
        return response_decoded.get('response', response_decoded.get('error')), response_decoded['code']
