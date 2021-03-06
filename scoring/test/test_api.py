#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import datetime
import unittest
import unittest.mock
import pathlib
import shutil
import json

import api
import store
from test_base import cases, ManageKVS, ManageAPI


class TestSuite(object):
    @classmethod
    def setUpClass(cls):
        cls.store.set('i:0', '["cars", "pets"]')
        cls.store.set('i:1', '["travel", "hi-tech"]')
        cls.store.set('i:2', '["sport", "music"]')
        cls.store.set('i:3', '["books", "tv"]')

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            hash_str = datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT
        else:
            hash_str = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(hash_str.encode('utf-8')).hexdigest()

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)

    @cases([
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "token": "",
            "arguments": {}
        },
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "token": "sdd",
            "arguments": {}
        },
        {
            "account": "horns&hoofs",
            "login": "admin",
            "method": "online_score",
            "token": "",
            "arguments": {}
        },
    ])
    def test_bad_auth(self, request):
        _, code = self.get_response(request)
        self.assertEqual(api.FORBIDDEN, code, msg=request)

    @cases([
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score"
        },
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "arguments": {}
        },
        {
            "account": "horns&hoofs",
            "method": "online_score",
            "arguments": {}
        },
    ])
    def test_invalid_method_request(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, msg=request)
        self.assertTrue(len(response), msg=request)

    @cases([
        {},
        {
            "phone": "79175002040"
        },
        {
            "phone": "89175002040",
            "email": "stupnikov@otus.ru"
        },
        {
            "phone": "79175002040",
            "email": "stupnikovotus.ru"
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": -1
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": "1"
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.1890"
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "XXX"
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": 1
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": "s",
            "last_name": 2
        },
        {
            "phone": "79175002040",
            "birthday": "01.01.2000",
            "first_name": "s"
        },
        {
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "last_name": 2
        },
    ])
    def test_invalid_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, msg=request)
        self.assertTrue(len(response))

    @cases([
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru"
        },
        {
            "phone": 79175002040,
            "email": "stupnikov@otus.ru"
        },
        {
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": "a",
            "last_name": "b"
        },
        {
            "gender": 0,
            "birthday": "01.01.2000"
        },
        {
            "gender": 2,
            "birthday": "01.01.2000"
        },
        {
            "first_name": "a",
            "last_name": "b"
        },
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "gender": 1,
            "birthday": "01.01.2000",
            "first_name": "a",
            "last_name": "b"
        },
    ])
    def test_ok_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code, msg=request)
        score = response.get("score")
        self.assertTrue(isinstance(score, (int, float)) and score >= 0, msg=request)
        if hasattr(self, 'context'):
            self.assertEqual(sorted(self.context["has"]), sorted(arguments.keys()), msg=request)

    def test_ok_score_admin_request(self):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)
        score = response.get("score")
        self.assertEqual(score, 42)

    @cases([
        {},
        {
            "date": "20.07.2017"
        },
        {
            "client_ids": [],
            "date": "20.07.2017"
        },
        {
            "client_ids": {
                1: 2
            },
            "date": "20.07.2017"
        },
        {
            "client_ids": ["1", "2"],
            "date": "20.07.2017"
        },
        {
            "client_ids": [1, 2],
            "date": "XXX"
        },
    ])
    def test_invalid_interests_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, msg=request)
        self.assertTrue(len(response), msg=request)

    @cases([
        {
            "client_ids": [1, 2, 3],
            "date": datetime.datetime.today().strftime("%d.%m.%Y")
        },
        {
            "client_ids": [1, 2],
            "date": "19.07.2017"
        },
        {
            "client_ids": [0]
        },
    ])
    def test_ok_interests_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code, msg=request)
        self.assertEqual(len(arguments["client_ids"]), len(response), msg=request)
        self.assertTrue(
            all(v and isinstance(v, list) and all(isinstance(i, str) for i in v) for v in response.values()),
            msg=request)
        if hasattr(self, 'context'):
            self.assertEqual(self.context.get("nclients"), len(arguments["client_ids"]), msg=request)


class TestIntegrationSuite(TestSuite, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = pathlib.Path('./test_api_integration')
        if cls.root.is_dir():
            shutil.rmtree(str(cls.root))
        cls.root.mkdir(parents=True)
        cls.kvs = ManageKVS(8012, cls.root)
        cls.api = ManageAPI(8082, cls.root, 'localhost,8012,10,3')
        cls.kvs.start()
        cls.api.start()
        cls.store = store.StoreKVS('localhost', 8012)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.api.stop()
        cls.kvs.stop()
        if cls.root.is_dir():
            shutil.rmtree(str(cls.root))

    def get_response(self, request):
        response = self.api.make_request('/method', json.dumps(request))
        response_decoded = json.loads(response.read().decode('utf-8'))
        return response_decoded.get('response', response_decoded.get('error')), response_decoded['code']


class TestMethodSuite(TestSuite, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = store.StoreMemory()
        super().setUpClass()

    def setUp(self):
        self.context = {}
        self.headers = {}

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)
