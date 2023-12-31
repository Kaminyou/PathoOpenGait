from marshmallow import Schema, fields
from marshmallow.decorators import post_load
from marshmallow.validate import Length

from enums.user import UserCategoryEnum
from security import get_sha256


class UserSchema(Schema):
    account = fields.Str(required=True, validate=Length(max=80))
    password = fields.Str(required=True, validate=Length(max=80))
    email = fields.Email(required=False, validate=Length(max=100))
    category = fields.Enum(UserCategoryEnum, required=True)

    @post_load
    def hash_password(self, data, **kwargs):
        data['password'] = get_sha256(data['password'])
        return data
