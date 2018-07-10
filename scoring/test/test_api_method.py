#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import api
import store
import test_api


class TestSuite(test_api.TestSuite, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = store.StoreMemory()
        super().setUpClass()

    def setUp(self):
        self.context = {}
        self.headers = {}

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)
