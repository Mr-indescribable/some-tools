#!/usr/bin/python3.6
#coding: utf-8

import json


class ObjectifiedDict():

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None

    @staticmethod
    def _convert(item):
        if isinstance(item, dict):
            return ObjectifiedDict(**item)
        if isinstance(item, list):
            return [ObjectifiedDict._convert(unit) for unit in item]
        if isinstance(item, tuple):
            return (ObjectifiedDict._convert(unit) for unit in item)
        if isinstance(item, set):
            return {ObjectifiedDict._convert(unit) for unit in item}
        else:
            return item

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = self._convert(value)

    def __iter__(self):
        return iter(
            self.__dict__.items()
        )

    def __bool__(self):
        return bool(self.__dict__)

    def __clear__(self):
        self.__dict__.clear()

    @staticmethod
    def _to_dumpable(item):
        if item.__class__ is bytes:
            return '<bytes length=%d>' % len(item)
        elif isinstance(item, ObjectifiedDict):
            return item.__str_assist__()
        elif item.__class__ in (list, tuple, set):
            return [ObjectifiedDict._to_dumpable(unit) for unit in item]
        elif item.__class__ not in (int, str, None):
            return str(item)
        return item

    def __str_assist__(self):
        d = {}
        for key, value in self.__dict__.items():
            d[key] = self._to_dumpable(value)
        return d

    def __str__(self):
        return json.dumps(
            self.__str_assist__(), indent=4
        )
