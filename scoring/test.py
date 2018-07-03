#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import datetime
import functools
import unittest
import unittest.mock

import api
import store


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c, ))
                f(*new_args)

        return wrapper

    return decorator


class TestStoreMemory(unittest.TestCase):
    def test_empty_cache(self):
        store_object = store.StoreMemory()
        self.assertIsNone(store_object.cache_get("123"))

    @cases([123, "123", None, {}, []])
    def test_set_get_cache(self, value):
        store_object = store.StoreMemory()
        store_object.cache_set("123", value, None)
        self.assertEqual(store_object.cache_get("123"), value, msg=value)

    def test_set_get_cache_dict(self):
        store_object = store.StoreMemory()
        store_object.cache_set("123", {'a': 1, 'b': 2}, None)
        self.assertDictEqual(store_object.cache_get("123"), {'a': 1, 'b': 2})

    def test_set_get_cache_list(self):
        store_object = store.StoreMemory()
        store_object.cache_set("123", ['a', 1, 'b', 2], None)
        self.assertListEqual(store_object.cache_get("123"), ['a', 1, 'b', 2])

    def test_set_get_cache_tuple(self):
        store_object = store.StoreMemory()
        store_object.cache_set("123", ('a', 1, 'b', 2), None)
        self.assertTupleEqual(store_object.cache_get("123"), ('a', 1, 'b', 2))

    def test_cache_expire(self):
        store_object = store.StoreMemory()
        with unittest.mock.patch('time.time', return_value=0) as mock:
            store_object.cache_set("123", 123, 10)
        with unittest.mock.patch('time.time', return_value=5.0) as mock:
            self.assertEqual(store_object.cache_get("123"), 123)
        with unittest.mock.patch('time.time', return_value=15.0) as mock:
            self.assertIsNone(store_object.cache_get("123"))

    def test_cache_unexpire(self):
        store_object = store.StoreMemory()
        with unittest.mock.patch('time.time', return_value=0) as mock:
            store_object.cache_set("123", 123, None)
        with unittest.mock.patch('time.time', return_value=float("inf")) as mock:
            self.assertEqual(store_object.cache_get("123"), 123)

    def test_empty_data(self):
        store_object = store.StoreMemory()
        with self.assertRaises(KeyError):
            store_object.get("123")

    @cases([
        123,
        "123",
        None,
    ])
    def test_set_get_data(self, value):
        store_object = store.StoreMemory()
        store_object.set("123", value)
        self.assertEqual(store_object.get("123"), value, msg=value)

    def test_set_get_data_dict(self):
        store_object = store.StoreMemory()
        store_object.set("123", {'a': 1, 'b': 2})
        self.assertDictEqual(store_object.get("123"), {'a': 1, 'b': 2})

    def test_set_get_data_list(self):
        store_object = store.StoreMemory()
        store_object.set("123", ['a', 1, 'b', 2])
        self.assertListEqual(store_object.get("123"), ['a', 1, 'b', 2])

    def test_set_get_data_tuple(self):
        store_object = store.StoreMemory()
        store_object.set("123", ('a', 1, 'b', 2))
        self.assertTupleEqual(store_object.get("123"), ('a', 1, 'b', 2))


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = store.StoreMemory()
        self.store.set('i:0', '["cars", "pets"]')
        self.store.set('i:1', '["travel", "hi-tech"]')
        self.store.set('i:2', '["sport", "music"]')
        self.store.set('i:3', '["books", "tv"]')

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

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
        self.assertEqual(self.context.get("nclients"), len(arguments["client_ids"]), msg=request)


if __name__ == "__main__":
    unittest.main()
