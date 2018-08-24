#!/usr/bin/python3.6
#coding: utf-8

from functools import wraps
from flask import request

from . import JsonSchemaValidator


def json_schema_verified(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        route = request.path
        json = request.get_json()

        JsonSchemaValidator.validate(route, json)
        return func(*args, **kwargs)
