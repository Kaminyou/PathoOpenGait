from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token, get_jwt, get_jwt_identity, jwt_required, unset_jwt_cookies,
)

from enums.user import UserCategoryEnum
from models import UserModel
from parsers.parser import parse_user_instances
from schemas.user import UserSchema
from security import get_sha256


admin_api = Blueprint('admin', __name__)
user_schema = UserSchema()


@admin_api.route("/whoami", methods=['GET'])
def admin_whoami():
    return {'msg': 'admin'}


@admin_api.route('/listuser', methods=['GET'])
@jwt_required()
def list_current_users():
    '''
    Enable admin to get a list of registered users.
    '''
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
        
        if user_instance.__dict__['category'] != UserCategoryEnum.admin:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        user_instances = UserModel.find_all_users()
        return {"currentUsers": parse_user_instances(user_instances)}, HTTPStatus.OK

    except Exception as e:
        current_app.logger.info(f'{account} trigger exception {e}')
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR


@admin_api.route('/createuser', methods=['POST'])
@jwt_required()
def create_user():
    '''
    Enable admin to create new user.
    '''
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
        
        if user_instance.__dict__['category'] != UserCategoryEnum.admin:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        new_user_account = request.form["account"]
        if UserModel.find_by_account(account=new_user_account) is not None:
            return {"msg": "Duplicated account"}, HTTPStatus.FORBIDDEN
        
        formData = user_schema.load(request.form)
        userObj = UserModel(**formData)
        try:
            userObj.save_to_db()

        except Exception:
            userObj.delete_from_db()  # Rollback
            raise ValueError

        return {"msg": "Success"}, HTTPStatus.OK

    except Exception as e:
        print(e)
        return {"message": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR


@admin_api.route('/changepwd', methods=['POST'])
@jwt_required()
def change_user_password():
    '''
    Enable admin to change any user's password.
    '''
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
        
        if user_instance.__dict__['category'] != UserCategoryEnum.admin:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        user_account = request.form["account"]
        new_password = request.form["password"]
        if UserModel.find_by_account(account=user_account) is None:
            return {"msg": "Does not exist"}, HTTPStatus.FORBIDDEN

        try:
            UserModel.reset_password(account=user_account, password=get_sha256(new_password))
        except Exception:
            raise ValueError

        return {"msg": "Success"}, HTTPStatus.OK

    except Exception:
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR
