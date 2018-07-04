#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
import time
import collections
import json
from http.client import HTTPConnection


class StoreBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def cache_get(self, key):
        pass

    @abc.abstractmethod
    def cache_set(self, key, value, timeout):
        pass

    @abc.abstractmethod
    def get(self, key):
        pass

    @abc.abstractmethod
    def set(self, key, value):
        pass


class StoreMemory(metaclass=abc.ABCMeta):
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


StoreMemory.register(StoreBase)


class StoreKVS(metaclass=abc.ABCMeta):
    Response = collections.namedtuple('Response', 'value success')

    def __init__(self, host, port, timeout, tries):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.tries = tries

    def make_request(self, method, request):
        for try_num in range(0, self.tries):
            try:
                connect = HTTPConnection(self.host, self.port, self.timeout)
                connect.request('POST', '/' + method, json.dumps(request))
                response = json.loads(connect.getresponse().read().decode('utf-8'))
                if 'code' in response and response['code'] == 200 and 'response' in response:
                    value = response['response']
                return self.Response(value, True)
            except:
                pass
        return self.Response(None, False)

    def cache_get(self, key):
        request = {
            'key': key,
        }
        response = self.make_request('cache_get', request)
        return response.value

    def cache_set(self, key, value, timeout):
        request = {'key': key, 'value': value, 'timeout': timeout}
        response = self.make_request('cache_set', request)

    def get(self, key):
        request = {
            'key': key,
        }
        response = self.make_request('data_get', request)
        if not response.success:
            raise KeyError
        return response.value

    def set(self, key, value):
        request = {'key': key, 'value': value}
        response = self.make_request('data_set', request)
        if not response.success:
            raise ValueError


StoreKVS.register(StoreBase)

s = StoreKVS('localhost', 8080, None, 3)

# s.set('key2', 'value2')

print(s.get('key2'))
print(s.get('key'))
