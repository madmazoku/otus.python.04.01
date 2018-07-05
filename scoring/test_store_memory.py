#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import unittest.mock

import store
from test_base import cases


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


if __name__ == "__main__":
    unittest.main()
