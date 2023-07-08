import os
from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token, get_jwt, get_jwt_identity, jwt_required, unset_jwt_cookies,
)

from enums.request import Status
from enums.user import UserCategoryEnum
from inference.tasks import inference_gait_task
from models import SubordinateModel, UserModel, RequestModel, ResultModel, ProfileModel
from parsers.parser import parse_subordinate_instances, parse_personal_profile, parse_request_instances
from schemas.subordinate import SubordinateSchema
from schemas.user import UserSchema
from schemas.request import RequestSchema
from security import get_sha256


manager_api = Blueprint('manager', __name__)
user_schema = UserSchema()
request_schema = RequestSchema()
subordinate_schema = SubordinateSchema()


@manager_api.route("/whoami", methods=['GET'])
def admin_whoami():
    return {'msg': 'manager'}


@manager_api.route('/listuser', methods=['GET'])
@jwt_required()
def list_manager_subordinates():
    '''
    Enable admin to get a list of registered users.
    '''
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        if user_instance.__dict__['category'] != UserCategoryEnum.manager:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        subordinate_instances = SubordinateModel.find_by_account(account=account)
        return {"currentUsers": parse_subordinate_instances(subordinate_instances)}, HTTPStatus.OK

    except Exception as e:
        current_app.logger.info(f'{account} trigger exception {e}')
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR


@manager_api.route('/createuser', methods=['POST'])
@jwt_required()
def create_subordinate():
    '''
    Enable admin to create new user.
    '''
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        if user_instance.__dict__['category'] != UserCategoryEnum.manager:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        new_user_account = request.form["account"]
        if UserModel.find_by_account(account=new_user_account) is not None:
            return {"msg": "Duplicated account"}, HTTPStatus.FORBIDDEN

        formData = user_schema.load(request.form)
        userObj = UserModel(**formData)

        subordinate_data = subordinate_schema.load(
            {
                'account': account,
                'subordinate': new_user_account
            }
        )

        subordinateObj = SubordinateModel(**subordinate_data)
        try:
            userObj.save_to_db()
            subordinateObj.save_to_db()

        except Exception:
            userObj.delete_from_db()  # Rollback
            subordinateObj.delete_from_db()

            raise ValueError

        return {"msg": "Success"}, HTTPStatus.OK

    except Exception as e:
        current_app.logger.info(f'{account} trigger exception {e}')
        return {"message": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR


@manager_api.route('/changepwd', methods=['POST'])
@jwt_required()
def change_subordinate_password():
    '''
    Enable admin to change any user's password.
    '''
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        if user_instance.__dict__['category'] != UserCategoryEnum.manager:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        user_account = request.form["account"]
        new_password = request.form["password"]
        if SubordinateModel.find_by_account_and_subordinate(account=account, subordinate=user_account) is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        if UserModel.find_by_account(account=user_account) is None:
            return {"msg": "Does not exist"}, HTTPStatus.FORBIDDEN

        try:
            UserModel.reset_password(account=user_account, password=get_sha256(new_password))
        except Exception:
            raise ValueError

        return {"msg": "Success"}, HTTPStatus.OK

    except Exception as e:
        current_app.logger.info(f'{account} trigger exception {e}')
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR


@manager_api.route('/upload/gait', methods=['POST'])
@jwt_required()
def manager_upload_gait_csv():
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        if user_instance.__dict__['category'] != UserCategoryEnum.manager:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        request_form = request.form.to_dict()
        target_account = request_form['account']  # should be subordinate
        request_form.pop('account', None)
        if SubordinateModel.find_by_account_and_subordinate(account=account, subordinate=target_account) is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        form_data = request_schema.load(request_form)
        form_data.update({"account": target_account})
        request_obj = RequestModel(**form_data)

        submit_uuid = request_obj.submitUUID

        csv_file = request.files['csvFile']
        mp4_file = request.files['mp4File']

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

    except Exception as e:
        current_app.logger.info(f'{account} trigger exception {e}')
        return (
            {'msg': 'Error'},
            HTTPStatus.FORBIDDEN,
        )
    

@manager_api.route('/request/results', methods=['POST'])
@jwt_required()
def manager_request_results():
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
        
        if user_instance.__dict__['category'] != UserCategoryEnum.manager:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
    
        target_account = request.form['account']
        if SubordinateModel.find_by_account_and_subordinate(account=account, subordinate=target_account) is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        request_objects = RequestModel.find_by_account_and_sort_by_exp_date(account=target_account)
        results = []
        for request_object in request_objects:
            if request_object.__dict__['status'] != Status.DONE:
                continue
            sub_results = {}
            sub_results['dateUpload'] = request_object.__dict__['dateUpload'].strftime("%Y-%m-%d")
            sub_results['date'] = request_object.__dict__['date'].strftime("%Y-%m-%d")
            request_uuid = request_object.__dict__['submitUUID']
            sub_results['detail'] = request_uuid
            result_objects = ResultModel.find_by_requestUUID(requestUUID=request_uuid)
            for result_object in result_objects:
                k = result_object.__dict__['resultKey']
                v = result_object.__dict__['resultValue']
                v_type = result_object.__dict__['resultType']
                if v_type == 'float':
                    v = round(float(v), 2)
                sub_results[k] = v
            results.append(sub_results)
        
        return (
            {
                'msg': 'success',
                'results': results,
            },
            HTTPStatus.OK,
        )

    except Exception as e:
        current_app.logger.info(f'{account} trigger exception {e}')
        return (
            {'msg': 'Error'},
            HTTPStatus.FORBIDDEN,
        )


@manager_api.route('/request/status', methods=['GET'])
@jwt_required()
def manager_request_status():
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        if user_instance.__dict__['category'] != UserCategoryEnum.manager:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
        
        request_objects = []
        subordinate_instances = SubordinateModel.find_by_account(account=account)
        for subordinate_instance in subordinate_instances:
            if subordinate_instance.__dict__['exist']:
                target_account = subordinate_instance.__dict__['subordinate']
                request_objects += RequestModel.find_by_account(account=target_account)
        request_status_data = parse_request_instances(request_objects)
        
        return (
            {
                'msg': 'success',
                'records': request_status_data,
            },
            HTTPStatus.OK,
        )

    except Exception as e:
        current_app.logger.info(f'{account} trigger exception {e}')
        return (
            {'msg': 'Error'},
            HTTPStatus.FORBIDDEN,
        )


@manager_api.route('/profile/personal', methods=['POST'])
@jwt_required()
def manager_get_user_profile():
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
        
        if user_instance.__dict__['category'] != UserCategoryEnum.manager:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
    
        target_account = request.form['account']
        if SubordinateModel.find_by_account_and_subordinate(account=account, subordinate=target_account) is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
        
        profile_object = ProfileModel.find_latest_by_account(account=target_account)
        profile = parse_personal_profile(profile_object)
        try:
            return jsonify({"msg": "Submit successfully!", "profile": profile}), HTTPStatus.OK

        except Exception as e:
            current_app.logger.info(f'{account} trigger exception {e}')
            return {"message": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR
    
    except Exception:
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR