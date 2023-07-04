from marshmallow import Schema, fields
from marshmallow.decorators import post_load
from marshmallow.validate import Length, Range

from security import get_uuid


class RequestSchema(Schema):
    dataType = fields.Str(required=True, validate=Length(max=100))
    modelName = fields.Str(required=True, validate=Length(max=100))
    date = fields.Date(required=True)
    description = fields.Str(required=False, validate=Length(max=200))

    @post_load
    def add_uuid(self, data, **kwargs):
        data["submitUUID"] = get_uuid()
        data["toShow"] = True
        return data
