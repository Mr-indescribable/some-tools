#!/usr/bin/python3.6
#coding: utf-8

import re

from werkzeug.exceptions import (
    BadRequest,
    UnprocessableEntity,
)


__all__ = [
    'Float',
    'Integer',
    'String',
    'Boolean',
    'Array',
    'ContainerArray',
    'Json',
]


class _JTypeMixin():

    def __init__(self, minimum=None, maximum=None, nullable=False):
        ''' Constructor

        :param minimum: minimum size of value
        :param maximum: maximum size of value
        :param nullable: specify whether the field could be null or not exists
        '''

        self.minimum = minimum
        self.maximum = maximum
        self.nullable = nullable

    def verify_type(self, value):
        if not isinstance(value, self.PY_TYPE):
            raise BadRequest

    def verify_value(self, value):
        pass

    def verify(self, value):
        ''' entrance of verification
        '''

        if self.nullable and value is None:
            return

        self.verify_type(value)
        self.verify_value(value)


class Float(_JTypeMixin):

    PY_TYPE = float

    def verify_value(self, value):
        if self.minimum is not None and value < self.minimum:
            raise UnprocessableEntity
        if self.maximum is not None and value > self.maximum:
            raise UnprocessableEntity


class Integer(Float):

    PY_TYPE = int


class String(_JTypeMixin):

    PY_TYPE = str

    def __init__(self, max_len=None, schema=None, nullable=False):
        ''' Constructor

        :param max_len: maximum length
        :param schema: schema of the String, it could be regex string or
                      compiled regex object (from re.compile)
        '''

        self.minimum = 0
        self.maximum = max_len
        self.schema = schema
        self.nullable = nullable

    def verify_value(self, value):
        if max_len is not None:
            if not self.minimum <= len(value) <= self.maximum:
                raise UnprocessableEntity

        if self.schema is not None:
            if not re.match(self.schema, value):
                raise UnprocessableEntity


class Boolean(_JTypeMixin):

    PY_TYPE = bool

    def __init__(self, nullable=False):
        self.nullable = nullable


class Array(_JTypeMixin):

    PY_TYPE = list

    def __init__(
        self, min_len=None, max_len=None, nullable=False, array_schema=None
    ):
        ''' Constructor

        :param min_len: minimum length
        :param max_len: maximum length
        :param array_schema: schema of the array，list type，
                             items in this list should be instances of JsonTypes
        '''

        self.minimum = min_len
        self.maximum = max_len
        self.nullable = nullable
        self.array_schema = array_schema

        if not isinstance(self.array_schema, list):
            raise TypeError('array_schema must be a list')

    def verify_array(self, array):
        if self.array_schema is None:
            return

        for jtype, item in zip(self.array_schema, array):
            jtype.verify(item)

    def verify_value(self, value):
        if self.maximum is None:
            return

        if not self.minimum <= len(value) <= self.maximum:
            raise UnprocessableEntity

    def verify(self, value):
        if self.nullable and value is None:
            return

        self.verify_type(value)
        self.verify_value(value)
        self.verify_array(value)


class ContainerArray(Array):

    ''' Container Array

    As a container, a container array should contain multiple items that
    with a same schema.
    '''

    PY_TYPE = list

    def __init__(self, item_schema, min_len=None, max_len=None, nullable=False):
        ''' Constructor

        :param item_schema: the schema of items in the array.
                            It could be one of json types defined in this module
        :param max_len: the max length of the array, None is equal to unlimited
        :param nullable: whet
        '''

        self.minimum = min_len
        self.maximum = max_len
        self.nullable = nullable
        self.item_schema = item_schema

    def verify_array(self, array):
        for item in array:
            self.item_schema.verify(item)


class Json(_JTypeMixin):

    PY_TYPE = dict

    # If there is a "nullable" field in the json, then we can do this to
    # evade the confliction: Json(False, **schema)
    def __init__(self, nullable=False, **json_schema):
        if len(json_schema) == 0:
            raise NotImplementedError('Invalid json_schema')

        self.nullable = nullable
        self.json_schema = json_schema

    def verify_json(self, json):
        for name, jtype in self.json_schema.items():
            value = json.get(name)
            jtype.verify(value)

    def verify(self, value):
        if self.nullable and value is None:
            return

        self.verify_type(value)
        self.verify_value(value)
        self.verify_json(value)
