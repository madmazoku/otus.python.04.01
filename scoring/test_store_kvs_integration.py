#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import unittest.mock
import http.client

import store
from test_base import cases


class TestSuite(unittest.TestCase):
    def setUp(self):
        print("setUp")

    def tearDown(self):
        print("tearDown")


if __name__ == "__main__":
    unittest.main()
