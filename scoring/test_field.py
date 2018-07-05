#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import unittest
import unittest.mock

import field
from test_base import cases


class TestField(unittest.TestCase):
    @cases([
        (field.Field(field_name='test'), {
            'comment': 'default'
        }),
        (field.Field(field_name='test'), {
            'test': None,
            'comment': 'default'
        }),
        (field.Field(required=True, nullable=True, field_name='test'), {
            'comment': 'required, nullable'
        }),
        (field.Field(required=True, nullable=False, field_name='test'), {
            'test': None,
            'comment': 'required, not nullable'
        }),
        (field.Field(required=False, nullable=False, field_name='test'), {
            'comment': 'not required, not nullable'
        }),
        (field.CharField(field_name='test'), {
            'test': 123
        }),
        (field.ArgumentsField(field_name='test'), {
            'test': []
        }),
        (field.EmailField(field_name='test'), {
            'test': 'aaa.bbb.ccc'
        }),
        (field.PhoneField(field_name='test'), {
            'test': 'abcdefghjik'
        }),
        (field.PhoneField(field_name='test'), {
            'test': '7123456789'
        }),
        (field.PhoneField(field_name='test'), {
            'test': '81234567890'
        }),
        (field.DateField(field_name='test'), {
            'test': '2018-02-20'
        }),
        (field.DateField(field_name='test'), {
            'test': '02.20.2018'
        }),
        (field.BirthDayField(field_name='test'), {
            'test': '20022018'
        }),
        (field.GenderField(field_name='test'), {
            'test': -1
        }),
        (field.GenderField(field_name='test'), {
            'test': 4
        }),
        (field.GenderField(field_name='test'), {
            'test': '0'
        }),
        (field.ClientIDsField(field_name='test'), {
            'test': {}
        }),
        (field.ClientIDsField(field_name='test'), {
            'test': [1, '2', 3]
        }),
    ])
    def test_field_invalid(self, field_object, struct):
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), struct)):
            field_object.validate(struct)

    def test_field_invalid_birthday(self):
        field_object = field.BirthDayField(field_name='test')
        today = datetime.date.today()
        value = today.replace(year=today.year - 71) - datetime.timedelta(days=1)
        struct = {'test': value.strftime('%d.%m.%Y')}
        with self.assertRaises(ValueError, msg="{!s} / {!s}".format(type(field_object), struct)):
            field_object.validate(struct)

    @cases([
        (field.Field(required=False, nullable=True, field_name='test'), {
            'comment': 'not required, nullable'
        }, None),
        (field.Field(required=False, nullable=True, field_name='test'), {
            'test': None,
            'comment': 'not required, nullable'
        }, None),
        (field.Field(field_name='test'), {
            'test': 1
        }, 1),
        (field.CharField(field_name='test'), {
            'test': ''
        }, ''),
        (field.CharField(field_name='test'), {
            'test': '123'
        }, '123'),
        (field.EmailField(field_name='test'), {
            'test': 'aaa@bbb.ccc'
        }, 'aaa@bbb.ccc'),
        (field.PhoneField(field_name='test'), {
            'test': '71234567890'
        }, '71234567890'),
        (field.PhoneField(field_name='test'), {
            'test': 71234567890
        }, '71234567890'),
        (field.DateField(field_name='test'), {
            'test': '20.02.2018'
        }, datetime.date(2018, 2, 20)),
        (field.GenderField(field_name='test'), {
            'test': 0
        }, 0),
        (field.GenderField(field_name='test'), {
            'test': 1
        }, 1),
        (field.GenderField(field_name='test'), {
            'test': 2
        }, 2),
    ])
    def test_field_valid(self, field_object, struct, value):
        self.assertEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field_object), struct, value))

    @cases([
        ({
            'test': {}
        }, {}),
        ({
            'test': {
                'f1': 1
            }
        }, {
            'f1': 1
        }),
    ])
    def test_field_valid_argument(self, struct, value):
        field_object = field.ArgumentsField(field_name='test')
        self.assertDictEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field), struct, value))

    def test_field_valid_birthday(self):
        field_object = field.BirthDayField(field_name='test')
        today = datetime.date.today()
        value = today.replace(year=today.year - 71) + datetime.timedelta(days=1)
        struct = {'test': value.strftime('%d.%m.%Y')}
        self.assertEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field), struct, value))

    @cases([
        ({
            'test': []
        }, []),
        ({
            'test': [1, 2, 3]
        }, [1, 2, 3]),
    ])
    def test_field_valid_client_ids(self, struct, value):
        field_object = field.ClientIDsField(field_name='test')
        self.assertListEqual(
            field_object.validate(struct), value, msg="{!s} / {!s} -> {!s}".format(type(field), struct, value))


if __name__ == "__main__":
    unittest.main()
