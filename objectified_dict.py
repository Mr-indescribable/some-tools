#!/usr/bin/python3.6
#coding: utf-8

import json


class ObjectifiedDict():

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __bool__(self):
        return bool(self.__dict__)

    def __clear__(self):
        self.__dict__.clear()

    def __str_assist__(self):
        d = {}
        for k, v in self.__dict__.items():
            if v.__class__ is bytes:
                v = '<bytes length=%d>' % len(v)
            elif isinstance(v, ObjectifiedDict):
                v = v.__str_assist__()
            elif v.__class__ not in (int, str, None):
                v = str(v)
            d[k] = v
        return d

    def __str__(self):
        return json.dumps(
            self.__str_assist__(), indent=4
        )
