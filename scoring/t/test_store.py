#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from test_base import cases


class TestSuite(object):
    def test_empty_cache(self):
        store_object = self.make_store()
        self.assertIsNone(store_object.cache_get("123"))

    @cases([123, "123", None, {}, []])
    def test_set_get_cache(self, value):
        store_object = self.make_store()
        store_object.cache_set("123", value, None)
        self.assertEqual(store_object.cache_get("123"), value, msg=value)

    def test_set_get_cache_dict(self):
        store_object = self.make_store()
        store_object.cache_set("123", {'a': 1, 'b': 2}, None)
        self.assertDictEqual(store_object.cache_get("123"), {'a': 1, 'b': 2})

    def test_set_get_cache_list(self):
        store_object = self.make_store()
        store_object.cache_set("123", ['a', 1, 'b', 2], None)
        self.assertListEqual(store_object.cache_get("123"), ['a', 1, 'b', 2])

    def test_empty_data(self):
        store_object = self.make_store()
        with self.assertRaises(KeyError):
            store_object.get("123")

    @cases([
        123,
        "123",
        None,
    ])
    def test_set_get_data(self, value):
        store_object = self.make_store()
        store_object.set("123", value)
        self.assertEqual(store_object.get("123"), value, msg=value)

    def test_set_get_data_dict(self):
        store_object = self.make_store()
        store_object.set("123", {'a': 1, 'b': 2})
        self.assertDictEqual(store_object.get("123"), {'a': 1, 'b': 2})

    def test_set_get_data_list(self):
        store_object = self.make_store()
        store_object.set("123", ['a', 1, 'b', 2])
        self.assertListEqual(store_object.get("123"), ['a', 1, 'b', 2])
