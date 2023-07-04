from marshmallow import Schema, fields
from marshmallow.decorators import post_load
from marshmallow.validate import Length, Range

from security import get_uuid


class ProfileSchema(Schema):
    name = fields.Str(allow_none=True, validate=Length(max=100))
    birthday = fields.Date(allow_none=True)
    diagnose = fields.Str(allow_none=True, validate=Length(max=100))
    stage = fields.Str(allow_none=True, validate=Length(max=100))
    dominantSide = fields.Str(allow_none=True, validate=Length(max=100))
    lded = fields.Str(allow_none=True, validate=Length(max=100))
    description = fields.Str(allow_none=True, validate=Length(max=200))

    @post_load
    def add_uuid(self, data, **kwargs):
        data["updateUUID"] = get_uuid()
        return data
