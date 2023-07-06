from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token, get_jwt, get_jwt_identity, jwt_required, unset_jwt_cookies,
)

from models import UserModel
from security import get_sha256


token_api = Blueprint('token', __name__)


@token_api.route('/login', methods=['POST'])
def login():
    '''
    Log in with account and password.
    If the user is authenticated, return the jwt token.
    '''
    try:
        account = request.json.get('account', None)
        password = request.json.get('password', None)

        if not UserModel.find_by_account(account=account):
            return (
                {'msg': 'Wrong account or password'},
                HTTPStatus.UNAUTHORIZED,
            )

        user_instance = UserModel.find_by_account(account=account)
        password_hash = user_instance.__dict__['password']
        if get_sha256(password) != password_hash:
            return (
                {'msg': 'Wrong account or password'},
                HTTPStatus.UNAUTHORIZED,
            )

        access_token = create_access_token(identity=account)
        response = {'msg': 'Success', 'access_token': access_token}
        return response, HTTPStatus.OK

    except Exception as e:
        current_app.logger.info(f'{account} trigger exception {e}')
        return (
            {'msg': 'Wrong account or password'},
            HTTPStatus.UNAUTHORIZED,
        )


@token_api.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'msg': 'Logout successful'})
    unset_jwt_cookies(response)
    return response, HTTPStatus.OK


@token_api.route('/validate', methods=['POST'])
@jwt_required()
def validate_token():
    '''
    Check if the given user and jwt token are all authenticated.
    '''
    try:
        account = get_jwt_identity()
        if not UserModel.find_by_account(account=account):
            return (
                {'msg': 'Wrong account or password'},
                HTTPStatus.UNAUTHORIZED,
            )

        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            return {'msg': 'Timeout'}, HTTPStatus.FORBIDDEN

        return {'msg': 'Success'}, HTTPStatus.OK

    except Exception as e:
        current_app.logger.info(f'{account} trigger exception {e}')
        return {'msg': 'Invalid'}, HTTPStatus.FORBIDDEN
