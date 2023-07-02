from marshmallow import Schema, fields
from marshmallow.decorators import post_load
from marshmallow.validate import Length, Range

from security import get_uuid


class RequestSchema(Schema):
    dataType = fields.Str(required=True, validate=Length(max=100))
    modelName = fields.Str(required=True, validate=Length(max=100))

    @post_load
    def add_uuid(self, data, **kwargs):
        data["submitUUID"] = get_uuid()
        return data
