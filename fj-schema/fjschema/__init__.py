#!/usr/bin/python3.6
#coding: utf-8


class BaseSchema():

    ''' The base class of all schema class
    '''

    @classmethod
    def verify(cls, value):
        cls.schema.verify(value)


class MetaSchema(type):

    ''' metaclass of all schema class

    Once use this class as a meta class, it will make your class inherit
    the BaseSchema class above and register your class in JsonSchemaValidator
    '''

    def __new__(mcls, name, bases, attrs, **kwargs):
        bases = list(bases)
        bases.append(BaseSchema)
        bases = tuple(bases)

        return type.__new__(mcls, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **kwargs):
        route = attrs.get('route')
        if route is None:
            raise NotImplementedError(
                'json schema class %s dosn\'t defined "route"' % name
            )

        JsonSchemaValidator.register(route, cls)


class JsonSchemaValidator():

    schema_mapping = {}

    @classmethod
    def register(cls, route, schema):
        cls.schema_mapping.update(
            {route: schema}
        )

    @classmethod
    def validate(cls, route, json):
        schema = cls.schema_mapping.get(route)
        if schema is None:
            raise RuntimeError(f'Unregistered schema: {route}')

        schema.verify(json)
