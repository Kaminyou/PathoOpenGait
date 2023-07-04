import os
from http import HTTPStatus

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import UserModel, RequestModel, ProfileModel
from schemas.request import RequestSchema
from schemas.profile import ProfileSchema
from inference.tasks import inference_gait_task
from security import get_sha256
from parsers.parser import parse_personal_profile

requestSchema = RequestSchema()
profileSchema = ProfileSchema()

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


@user_api.route('/upload/gait', methods=['POST'])
@jwt_required()
def upload_gait_csv():
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
        
        form_data = requestSchema.load(request.form)
        form_data.update({"account": account})
        request_obj = RequestModel(**form_data)
        

        submit_uuid = request_obj.submitUUID


        csv_file = request.files['csvFile']
        mp4_file = request.files['mp4File']
        # username = request.form.get('username')
        # birthday = request.form.get('birthday')
        # height = request.form.get('height')
        # description = request.form.get('description')
        # print(username, birthday, height, description)

        data_root = f'data/{submit_uuid}'
        os.makedirs(data_root)
        os.makedirs(os.path.join(data_root, 'csv'))
        os.makedirs(os.path.join(data_root, 'video'))
        csv_file.save(os.path.join(data_root, 'csv', 'uploaded.csv'))
        mp4_file.save(os.path.join(data_root, 'video', 'uploaded.mp4'))
        request_obj.save_to_db()
        try:
            task = inference_gait_task.delay(request_obj.submitUUID)
            return (
                {
                    'msg': 'File uploaded successfully',
                    'task_id': task.id,
                },
                HTTPStatus.OK,
            )

        except Exception:
            request_obj.delete_from_db()  # Rollback
            return {'msg': 'Internal Server Error!'}, HTTPStatus.INTERNAL_SERVER_ERROR


        return (
            {'msg': 'File uploaded successfully'},
            HTTPStatus.OK,
        )

    except Exception as e:
        user_api.logger.info(f'{account} trigger exception {e}')
        return (
            {'msg': 'Error'},
            HTTPStatus.FORBIDDEN,
        )


@user_api.route('/changepwd', methods=['POST'])
@jwt_required()
def change_user_password_personal():
    try:
        account = get_jwt_identity()
        if not UserModel.find_by_account(account=account):
            return {"msg": "Wrong account or password"}, 401
        new_password = request.form["password"]

        try:
            UserModel.reset_password(account=account, password=get_sha256(new_password))
        except Exception:
            raise ValueError

        return {"msg": "Success"}, HTTPStatus.OK

    except Exception:
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR


@user_api.route('/profile/update', methods=['POST'])
@jwt_required()
def update_user_profile():
    try:
        account = get_jwt_identity()
        if not UserModel.find_by_account(account=account):
            return {"msg": "Wrong account or password"}, 401

        form_data = {}
        for k, v in request.form.items():
            if v == '':
                form_data[k] = None
            else:
                form_data[k] = v
        form_data = profileSchema.load(form_data)
        form_data.update({"account": account})
        profile_obj = ProfileModel(**form_data)

        profile_obj.save_to_db()

        return {"msg": "Success"}, HTTPStatus.OK
    
    except Exception as e:
        print(e)
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR


@user_api.route('/profile/personal', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        account = get_jwt_identity()
        if not UserModel.find_by_account(account=account):
            return {"msg": "Wrong account or password"}, 401
        
        profile_object = ProfileModel.find_latest_by_account(account=account)
        profile = parse_personal_profile(profile_object)
        try:
            return jsonify({"msg": "Submit successfully!", "profile": profile}), HTTPStatus.OK

        except Exception as e:
            print(e)
            return {"message": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR
    
    except Exception:
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR
