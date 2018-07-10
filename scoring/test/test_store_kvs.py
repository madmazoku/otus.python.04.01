#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import unittest.mock

import store
from test_base import cases


class TestSuite(unittest.TestCase):
    def test_connect(self):
        with unittest.mock.patch('http.client.HTTPConnection', autospec=True) as mock_connection:
            store_object = store.StoreKVS('localhost', 8010)
            mock_connection.assert_called_once_with('localhost', 8010, 10)

    def test_retry_request(self):
        with unittest.mock.patch('http.client.HTTPConnection', autospec=True) as mock_connection:

            class HTTPResponseMock:
                def __init__(self, status, content):
                    self.status = status
                    self.content = content

                def read(self):
                    return self.content.encode('utf-8')

            mock_connection.return_value.getresponse.side_effect = [
                ConnectionError(),
                HTTPResponseMock(400, '{"code":400, "'),
                HTTPResponseMock(200, '{"code":200, "response": "response"}'),
            ]

            store_object = store.StoreKVS('localhost', 8010)
            response = store_object.make_request('/test', {'test': 'test'})
            mock_connection.return_value.request.assert_has_calls([
                unittest.mock.call('POST', '/test', '{"test": "test"}'),
                unittest.mock.call('POST', '/test', '{"test": "test"}'),
                unittest.mock.call('POST', '/test', '{"test": "test"}')
            ])
            self.assertEqual(response, 'response')

    def test_retry_request_fail(self):
        with unittest.mock.patch('http.client.HTTPConnection', autospec=True) as mock_connection:
            mock_connection.return_value.getresponse.side_effect = [
                ConnectionError(),
                ConnectionError(),
                ConnectionError(),
            ]

            store_object = store.StoreKVS('localhost', 8010)
            with self.assertRaises(ConnectionError):
                store_object.make_request('/test', {'test': 'test'})
            mock_connection.return_value.request.assert_has_calls([
                unittest.mock.call('POST', '/test', '{"test": "test"}'),
                unittest.mock.call('POST', '/test', '{"test": "test"}'),
                unittest.mock.call('POST', '/test', '{"test": "test"}')
            ])

    def test_cache_get_success(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = 'response'
            store_object = store.StoreKVS('localhost', 8010)
            value = store_object.cache_get('123')
            mock_make_request.assert_called_once_with(store_object, '/cache_get', {'key': '123'})
            self.assertEqual(value, 'response')

    def test_cache_get_fail(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.side_effect = ConnectionError
            store_object = store.StoreKVS('localhost', 8010)
            value = store_object.cache_get('123')
            mock_make_request.assert_called_once_with(store_object, '/cache_get', {'key': '123'})
            self.assertIsNone(value)

        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.side_effect = KeyError
            store_object = store.StoreKVS('localhost', 8010)
            value = store_object.cache_get('123')
            mock_make_request.assert_called_once_with(store_object, '/cache_get', {'key': '123'})
            self.assertIsNone(value)

    def test_cache_set_success(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = None
            store_object = store.StoreKVS('localhost', 8010)
            store_object.cache_set('123', 456, 789)
            mock_make_request.assert_called_once_with(store_object, '/cache_set', {
                'key': '123',
                'value': 456,
                'timeout': 789
            })

    def test_cache_set_fail(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.side_effect = ConnectionError
            store_object = store.StoreKVS('localhost', 8010)
            store_object.cache_set('123', 456, 789)
            mock_make_request.assert_called_once_with(store_object, '/cache_set', {
                'key': '123',
                'value': 456,
                'timeout': 789
            })

    def test_data_get_success(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = 'response'
            store_object = store.StoreKVS('localhost', 8010)
            value = store_object.get('123')
            mock_make_request.assert_called_once_with(store_object, '/data_get', {'key': '123'})
            self.assertEqual(value, 'response')

    def test_data_get_fail(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.side_effect = ConnectionError
            store_object = store.StoreKVS('localhost', 8010)
            with self.assertRaises(ConnectionError):
                store_object.get('123')
            mock_make_request.assert_called_once_with(store_object, '/data_get', {'key': '123'})

        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.side_effect = KeyError
            store_object = store.StoreKVS('localhost', 8010)
            with self.assertRaises(KeyError):
                store_object.get('123')
            mock_make_request.assert_called_once_with(store_object, '/data_get', {'key': '123'})

    def test_data_set_success(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = None
            store_object = store.StoreKVS('localhost', 8010)
            store_object.set('123', 456)
            mock_make_request.assert_called_once_with(store_object, '/data_set', {'key': '123', 'value': 456})

    def test_data_set_fail(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.side_effect = ConnectionError
            store_object = store.StoreKVS('localhost', 8010)
            with self.assertRaises(ConnectionError):
                store_object.set('123', 456)
            mock_make_request.assert_called_once_with(store_object, '/data_set', {'key': '123', 'value': 456})
