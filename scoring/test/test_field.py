#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import unittest

import field
from test_base import cases


class TestSuite(unittest.TestCase):
    @cases([({
        'field_name': 'test'
    }, {}), ({
        'field_name': 'test'
    }, {
        'test': None,
    }), ({
        'required': True,
        'nullable': True,
        'field_name': 'test'
    }, {}), ({
        'required': True,
        'nullable': False,
        'field_name': 'test'
    }, {
        'test': None,
    }), ({
        'required': False,
        'nullable': False,
        'field_name': 'test'
    }, {})])
    def test_field_invalid(self, field_kvargs, struct):
        field_object = field.Field(**field_kvargs)
        with self.assertRaises(ValueError, msg="{!s} : {!s} / {!s}".format(type(field_object), field_kvargs, struct)):
            field_object.validate(struct)

    @cases([
        [],
        {},
        123,
        123.456,
    ])
    def test_char_field_invalid(self, test):
        field_object = field.CharField(field_name='test')
        struct = {'test': test}
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), test)):
            field_object.validate(struct)

    @cases([
        [],
        123,
        123.456,
        '123.456',
    ])
    def test_arguments_field_invalid(self, test):
        field_object = field.ArgumentsField(field_name='test')
        struct = {'test': test}
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), test)):
            field_object.validate(struct)

    @cases([
        'aaa.bbb.ccc',
        'bbb@ccc',
    ])
    def test_email_field_invalid(self, test):
        field_object = field.EmailField(field_name='test')
        struct = {'test': test}
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), test)):
            field_object.validate(struct)

    @cases([
        'abcdefghjik',
        '7123456789',
        '81234567890',
    ])
    def test_phone_field_invalid(self, test):
        field_object = field.PhoneField(field_name='test')
        struct = {'test': test}
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), test)):
            field_object.validate(struct)

    @cases([
        '2018-02-20',
        '02.20.2018',
    ])
    def test_date_field_invalid(self, test):
        field_object = field.DateField(field_name='test')
        struct = {'test': test}
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), test)):
            field_object.validate(struct)

    def test_birthday_field_invalid(self):
        field_object = field.BirthDayField(field_name='test')
        today = datetime.date.today()
        value = today.replace(year=today.year - 71) - datetime.timedelta(days=1)
        test = value.strftime('%d.%m.%Y')
        struct = {'test': test}
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), test)):
            field_object.validate(struct)

    @cases([
        -1,
        4,
        '0',
    ])
    def test_gender_field_invalid(self, test):
        field_object = field.GenderField(field_name='test')
        struct = {'test': test}
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), test)):
            field_object.validate(struct)

    @cases([
        {},
        [1, '2', 3],
    ])
    def test_client_ids_field_invalid(self, test):
        field_object = field.ClientIDsField(field_name='test')
        struct = {'test': test}
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), test)):
            field_object.validate(struct)

    @cases([
        ({
            'required': False,
            'nullable': True,
            'field_name': 'test'
        }, {}, None),
        ({
            'required': False,
            'nullable': True,
            'field_name': 'test'
        }, {
            'test': None,
        }, None),
        ({
            'field_name': 'test'
        }, {
            'test': 1
        }, 1),
    ])
    def test_field_valid(self, field_kvargs, struct, value):
        field_object = field.Field(**field_kvargs)
        self.assertEqual(
            field_object.validate(struct),
            value,
            msg="{!s} : {!s} / {!s} -> {!s}".format(type(field_object), field_kvargs, struct, value))

    @cases([
        ('', ''),
        ('123', '123'),
    ])
    def test_char_field_valid(self, test, value):
        field_object = field.CharField(field_name='test')
        struct = {'test': test}
        self.assertEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field_object), test, value))

    @cases([
        ({}, {}),
        ({
            'f1': 1
        }, {
            'f1': 1
        }),
    ])
    def test_argument_field_valid(self, test, value):
        field_object = field.ArgumentsField(field_name='test')
        struct = {'test': test}
        self.assertDictEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field_object), test, value))

    @cases([
        ('aaa@bbb.ccc', 'aaa@bbb.ccc'),
        ('123 aaa@bbb.ccc', '123 aaa@bbb.ccc'),
    ])
    def test_email_field_valid(self, test, value):
        field_object = field.EmailField(field_name='test')
        struct = {'test': test}
        self.assertEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field_object), test, value))

    @cases([
        ('71234567890', '71234567890'),
        (71234567890, '71234567890'),
    ])
    def test_phone_field_valid(self, test, value):
        field_object = field.PhoneField(field_name='test')
        struct = {'test': test}
        self.assertEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field_object), test, value))

    @cases([
        ('20.02.2018', datetime.date(2018, 2, 20)),
        ('01.01.1931', datetime.date(1931, 1, 1)),
    ])
    def test_date_field_valid(self, test, value):
        field_object = field.DateField(field_name='test')
        struct = {'test': test}
        self.assertEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field_object), test, value))

    def test_field_valid_birthday(self):
        field_object = field.BirthDayField(field_name='test')
        today = datetime.date.today()
        value = today.replace(year=today.year - 71) + datetime.timedelta(days=1)
        test = value.strftime('%d.%m.%Y')
        struct = {'test': test}
        self.assertEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field_object), test, value))

    @cases([
        (0, 0),
        (1, 1),
        (2, 2),
    ])
    def test_gender_field_valid(self, test, value):
        field_object = field.GenderField(field_name='test')
        struct = {'test': test}
        self.assertEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field_object), test, value))

    @cases([
        ([], []),
        ([1, 2, 3], [1, 2, 3]),
    ])
    def test_client_ids_field_valid(self, test, value):
        field_object = field.ClientIDsField(field_name='test')
        struct = {'test': test}
        self.assertListEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field_object), test, value))
