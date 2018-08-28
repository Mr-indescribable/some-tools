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
        attr_str     = String(128, nullable=False),
        attr_int     = Integer(nullable=True),
        some_objects = ContainerArray(
                           item_schema=String(128, schema=r'^SomeRegex$'),
                           min_len=1,
                           max_len=10,
                           nullable=True,
                       ),
        nested_json  = Json(
                           attr0 = String(128),
                           attr1 = Integer(minimum=0, maximum=100),
                           attr2 = Float(minimum=0.1, maximum=0.9),
                       ),
    )
