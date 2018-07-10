#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import collections
import json
import http.client


class StoreMemory(object):
    CacheRecord = collections.namedtuple('CacheRecord', 'value expire')

    def __init__(self):
        self.data = {}
        self.cache = {}

    def cache_get(self, key):
        value = None
        if key in self.cache:
            record = self.cache[key]
            if record.expire is None or record.expire >= time.time():
                value = record.value
            else:
                del self.cache[key]
        return value

    def cache_set(self, key, value, timeout):
        self.cache[key] = self.CacheRecord(value, None if timeout is None else time.time() + timeout)

    def get(self, key):
        return self.data[key]

    def set(self, key, value):
        self.data[key] = value


class StoreKVS(object):
    def __init__(self, host, port, timeout=10, tries=3):
        self.host = host
        self.port = int(port)
        self.timeout = float(timeout)
        self.tries = int(tries)
        self.connect = http.client.HTTPConnection(self.host, self.port, self.timeout)

    def make_request(self, method, request):
        request_str = json.dumps(request)
        try_num = 0
        while (True):
            try_num += 1
            try:
                self.connect.request('POST', method, request_str)
                response = self.connect.getresponse()
                response_decoded = json.loads(response.read().decode('utf-8'))
                if response.status == 200 and 'response' in response_decoded:
                    return response_decoded['response']
                raise KeyError(response_decoded.get('error', 'kvs service invalid response'))
            except (ConnectionError, json.JSONDecodeError, KeyError):
                self.connect = http.client.HTTPConnection(self.host, self.port, self.timeout)
                if try_num < self.tries:
                    time.sleep(try_num * 0.1)
                else:
                    raise

    def cache_get(self, key):
        request = {
            'key': key,
        }
        try:
            return self.make_request('/cache_get', request)
        except (ConnectionError, KeyError):
            return None

    def cache_set(self, key, value, timeout):
        request = {'key': key, 'value': value, 'timeout': timeout}
        try:
            self.make_request('/cache_set', request)
        except (ConnectionError, KeyError):
            return None

    def get(self, key):
        request = {
            'key': key,
        }
        return self.make_request('/data_get', request)

    def set(self, key, value):
        request = {'key': key, 'value': value}
        self.make_request('/data_set', request)
