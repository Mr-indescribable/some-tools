#!/usr/bin/python3.6
#coding: utf-8


'''
step0: register error handlers in your flask app. fjschema raises werkzeug's HTTP excetion
       when the json schema verification dosn't passed. You need to handle the following exceptions:
           werkzeug.exceptions.BadRequest, werkzeug.UnprocessableEntity

       fjschema will raise BadRequest when any data type is not matched or required field is missing
       and raises UnprocessableEntity when any value is not match the size definition

step1: define a schema class like below
step2: load your schema class in your flask application by importing this .py file
step3: use fjschema.decorators.json_schema_verified on your view function
'''


from fjschema import MetaSchema
from fjschema.types import *


class JSchema0(metaclass=MetaSchema):

    # this is the route of your view function
    route = '/schema0'

    # this is the schema specification
    schema = Json(
        name   = String(128, nullable=False),
        height = Integer(nullable=False)
        weight = Integer(nullable=True),
    )
