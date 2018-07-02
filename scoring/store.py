#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 

import abc

class StoreBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_cache(self, key):
        pass
    @abc.abstractmethod
    def put_cache(self, key, value):
        pass
    @abc.abstractmethod
    def get(self, key):
        pass
    @abc.abstractmethod
    def put(self, key, value):
        pass


class StoreMemory(metaclass=abc.ABCMeta):
    data = {}
    cache = {}

    def get_cache(self, key):
        return cache[key]

    def put_cache(self, key, value):
        cache[key] = value

    def get(self, key):
        return data[key]

    def put(self, key, value):
        data[key] = value
