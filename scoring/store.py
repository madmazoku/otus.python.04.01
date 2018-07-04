#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
import time
import collections


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