from http import HTTPStatus

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import UserModel

user_api = Blueprint('user', __name__)


@user_api.route('/category', methods=['GET'])
@jwt_required()
def get_user_category() -> dict:
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        category = user_instance.__dict__['category'].value

        return (
            {'category': category},
            HTTPStatus.OK,
        )
    except Exception as e:
        user_api.logger.info(f'trigger exception {e}')
        return (
            {'category': 'guest'},
            HTTPStatus.OK,
        )
