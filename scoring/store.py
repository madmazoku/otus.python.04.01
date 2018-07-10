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
    Response = collections.namedtuple('Response', 'value success')

    def __init__(self, host, port, timeout = 10, tries = 3):
        self.host = host
        self.port = int(port)
        self.timeout = float(timeout)
        self.tries = int(tries)
        self.connect = http.client.HTTPConnection(self.host, self.port, self.timeout)

    def make_request(self, method, request):
        request_str = json.dumps(request)
        for try_num in range(0, self.tries):
            try:
                self.connect.request('POST', method, request_str)
                response = self.connect.getresponse()
                if response.status == 200:
                    response_decoded = json.loads(response.read().decode('utf-8'))
                    if 'response' in response_decoded:
                        return self.Response(response_decoded['response'], True)
                    else:
                        raise ValueError
                time.sleep((try_num + 1) * 0.1)
            except ConnectionError as e:
                self.connect = http.client.HTTPConnection(self.host, self.port, self.timeout)
        return self.Response(None, False)

    def cache_get(self, key):
        request = {
            'key': key,
        }
        response = self.make_request('/cache_get', request)
        return response.value

    def cache_set(self, key, value, timeout):
        request = {'key': key, 'value': value, 'timeout': timeout}
        response = self.make_request('/cache_set', request)

    def get(self, key):
        request = {
            'key': key,
        }
        response = self.make_request('/data_get', request)
        if not response.success:
            raise KeyError
        return response.value

    def set(self, key, value):
        request = {'key': key, 'value': value}
        response = self.make_request('/data_set', request)
        if not response.success:
            raise ValueError


