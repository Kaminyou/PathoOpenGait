from marshmallow import Schema, fields
from marshmallow.decorators import post_load
from marshmallow.validate import Length


class SubordinateSchema(Schema):
    account = fields.Str(required=True, validate=Length(max=80))
    subordinate = fields.Str(required=True, validate=Length(max=80))

    @post_load
    def add_exist(self, data, **kwargs):
        data['exist'] = True
        return data
