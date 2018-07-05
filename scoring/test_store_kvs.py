#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import unittest.mock
import http.client

import store
from test_base import cases


class TestSuite(unittest.TestCase):
    def test_connect(self):
        with unittest.mock.patch('http.client.HTTPConnection', autospec=True) as mock_connection:
            store_object = store.StoreKVS('localhost', 8010, 10, 3)
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
                HTTPResponseMock(400, '{"code":400, "response": null}'),
                HTTPResponseMock(200, '{"code":200, "response": "response"}'),
            ]

            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            response = store_object.make_request('/test', {'test': 'test'})
            mock_connection.return_value.request.assert_has_calls([
                unittest.mock.call('POST', '/test', '{"test": "test"}'),
                unittest.mock.call('POST', '/test', '{"test": "test"}'),
                unittest.mock.call('POST', '/test', '{"test": "test"}')
            ])
            self.assertEqual(response, store.StoreKVS.Response('response', True))

    def test_retry_request_fail(self):
        with unittest.mock.patch('http.client.HTTPConnection', autospec=True) as mock_connection:
            mock_connection.return_value.getresponse.side_effect = [
                ConnectionError(),
                ConnectionError(),
                ConnectionError(),
            ]

            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            response = store_object.make_request('/test', {'test': 'test'})
            mock_connection.return_value.request.assert_has_calls([
                unittest.mock.call('POST', '/test', '{"test": "test"}'),
                unittest.mock.call('POST', '/test', '{"test": "test"}'),
                unittest.mock.call('POST', '/test', '{"test": "test"}')
            ])
            self.assertEqual(response, store.StoreKVS.Response(None, False))

    def test_cache_get_success(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = store.StoreKVS.Response('response', True)
            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            value = store_object.cache_get('123')
            mock_make_request.assert_called_once_with(store_object, '/cache_get', {'key': '123'})
            self.assertEqual(value, 'response')

    def test_cache_get_fail(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = store.StoreKVS.Response(None, False)
            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            value = store_object.cache_get('123')
            mock_make_request.assert_called_once_with(store_object, '/cache_get', {'key': '123'})
            self.assertIsNone(value)

    def test_cache_set_success(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = store.StoreKVS.Response('response', True)
            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            store_object.cache_set('123', 456, 789)
            mock_make_request.assert_called_once_with(store_object, '/cache_set', {
                'key': '123',
                'value': 456,
                'timeout': 789
            })

    def test_cache_set_fail(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = store.StoreKVS.Response(None, False)
            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            store_object.cache_set('123', 456, 789)
            mock_make_request.assert_called_once_with(store_object, '/cache_set', {
                'key': '123',
                'value': 456,
                'timeout': 789
            })

    def test_data_get_success(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = store.StoreKVS.Response('response', True)
            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            value = store_object.get('123')
            mock_make_request.assert_called_once_with(store_object, '/data_get', {'key': '123'})
            self.assertEqual(value, 'response')

    def test_data_get_fail(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = store.StoreKVS.Response(None, False)
            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            with self.assertRaises(KeyError):
                store_object.get('123')
            mock_make_request.assert_called_once_with(store_object, '/data_get', {'key': '123'})

    def test_data_set_success(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = store.StoreKVS.Response('response', True)
            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            store_object.set('123', 456)
            mock_make_request.assert_called_once_with(store_object, '/data_set', {'key': '123', 'value': 456})

    def test_data_set_fail(self):
        with unittest.mock.patch('store.StoreKVS.make_request', autospec=True) as mock_make_request:
            mock_make_request.return_value = store.StoreKVS.Response(None, False)
            store_object = store.StoreKVS('localhost', 8010, 10, 3)
            with self.assertRaises(ValueError):
                store_object.set('123', 456)
            mock_make_request.assert_called_once_with(store_object, '/data_set', {'key': '123', 'value': 456})


if __name__ == "__main__":
    unittest.main()
