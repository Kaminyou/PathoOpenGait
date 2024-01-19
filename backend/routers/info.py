from http import HTTPStatus

from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from inference.config import get_data_types, get_model_names
from models import UserModel


info_api = Blueprint('info', __name__)


@info_api.route('/list/datatypes', methods=['GET'])
@jwt_required()
def get_data_type_list() -> dict:
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        data_types = get_data_types()
        return (
            {'datatypes': data_types},
            HTTPStatus.OK,
        )
    except Exception as e:
        current_app.logger.info(f'trigger exception {e}')
        return (
            {'datatypes': []},
            HTTPStatus.OK,
        )


@info_api.route('/list/modelnames', methods=['GET'])
@jwt_required()
def get_model_name_list() -> dict:
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        data_type = request.args.get('datatype')

        model_names = get_model_names(data_type)
        return (
            {'modelnames': model_names},
            HTTPStatus.OK,
        )
    except Exception as e:
        current_app.logger.info(f'trigger exception {e}')
        return (
            {'modelnames': []},
            HTTPStatus.OK,
        )
