#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import unittest.mock

import store
import test_store


class TestSuite(test_store.TestSuite, unittest.TestCase):
    def make_store(self):
        return store.StoreMemory()

    def test_cache_expire(self):
        store_object = self.make_store()
        with unittest.mock.patch('time.time', return_value=0) as mock:
            store_object.cache_set("123", 123, 10)
        with unittest.mock.patch('time.time', return_value=5.0) as mock:
            self.assertEqual(store_object.cache_get("123"), 123)
        with unittest.mock.patch('time.time', return_value=15.0) as mock:
            self.assertIsNone(store_object.cache_get("123"))

    def test_cache_unexpire(self):
        store_object = self.make_store()
        with unittest.mock.patch('time.time', return_value=0) as mock:
            store_object.cache_set("123", 123, None)
        with unittest.mock.patch('time.time', return_value=float("inf")) as mock:
            self.assertEqual(store_object.cache_get("123"), 123)
