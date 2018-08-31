#!/usr/bin/python3.6
#coding: utf-8


class _BaseEnum():

    def __contains__(cls, value):
        return value in cls.__members__.values()

    def __iter__(cls):
        return iter(cls.__members__.items())


class MetaEnum(type):

    ''' Meta class enumerations
    '''

    def __new__(mcls, name, bases, attrs):
        if '__members__' in attrs:
            raise AttributeError(
                '__members__ will be a built-in attribute of enum classes. '
                'It will cause conflictions if you use it in your enum class.'
            )

        original_attrs = dict(attrs)
        attrs.pop('__module__')
        attrs.pop('__qualname__')
        original_attrs.update(__members__=attrs)

        bases = list(bases)
        bases.append(_BaseEnum)
        bases = tuple(bases)

        # is returns an instance but not a class
        return type.__new__(mcls, name, bases, original_attrs)()
