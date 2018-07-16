#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import time
import pathlib
import shutil

import store
from test_base import ManageKVS
import test_store


class TestSuite(test_store.TestSuite, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = pathlib.Path('./test_store_kvs_integration')
        if cls.root.is_dir():
            shutil.rmtree(str(cls.root))
        cls.root.mkdir(parents=True)
        cls.kvs = ManageKVS(8011, cls.root)
        cls.kvs.start()

    @classmethod
    def tearDownClass(cls):
        cls.kvs.stop()
        if cls.root.is_dir():
            shutil.rmtree(str(cls.root))

    def make_store(self):
        return store.StoreKVS('localhost', 8011)

    def test_cache_expire(self):
        store_object = self.make_store()
        store_object.cache_set("123", 123, 0.5)
        self.assertEqual(store_object.cache_get("123"), 123)
        time.sleep(1)
        self.assertIsNone(store_object.cache_get("123"))
