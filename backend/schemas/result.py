from marshmallow import Schema, fields
from marshmallow.decorators import post_load
from marshmallow.validate import Length

from security import get_uuid


class ResultSchema(Schema):
    requestUUID = fields.Str(required=True, validate=Length(max=36))

    resultKey = fields.Str(required=True, validate=Length(max=100))
    resultValue = fields.Str(required=True, validate=Length(max=100))
    resultType = fields.Str(required=True, validate=Length(max=100))
    resultUnit = fields.Str(required=True, validate=Length(max=100))

    @post_load
    def add_uuid(self, data, **kwargs):
        data['resultUUID'] = get_uuid()
        return data
