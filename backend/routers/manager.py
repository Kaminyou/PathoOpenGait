import os
from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request, send_file, after_this_request
from flask_jwt_extended import (
    get_jwt_identity, jwt_required,
)


from enums.request import Status
from enums.user import UserCategoryEnum
from inference.tasks import inference_gait_task
from models import SubordinateModel, UserModel, RequestModel, ResultModel, ProfileModel
from parsers.parser import parse_subordinate_instances, parse_personal_profile, parse_request_instances
from schemas.subordinate import SubordinateSchema
from schemas.user import UserSchema
from schemas.request import RequestSchema
from security import get_sha256, generate_random_string


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
        try:
            csv_file.save(os.path.join(data_root, 'csv', 'uploaded.csv'))
        except Exception:
            current_app.logger.info(f'{account} submit with no 3D csv')
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


@manager_api.route('/request/report/download', methods=['GET'])
@jwt_required()
def manager_request_report_download():
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        if user_instance.__dict__['category'] != UserCategoryEnum.manager:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN
        
        subordinate_instances = SubordinateModel.find_by_account(account=account)

        csv = ''
        csv += 'account,name,gender,birthday,diagnose,stage,dominant_side,LDED,experiment_date,stride_length,stride_width,stride_time,velocity,cadence,turn_time\n'
        for subordinate_instance in subordinate_instances:
            if subordinate_instance.__dict__['exist']:
                target_account = subordinate_instance.__dict__['subordinate']
                profile_object = ProfileModel.find_latest_by_account(account=target_account)
                
                ss = f'{target_account},NA,NA,NA,NA,NA,NA,NA,'
                if profile_object:
                    name = profile_object.__dict__['name']
                    gender = profile_object.__dict__['gender']
                    birthday = profile_object.__dict__['birthday'].strftime("%Y-%m-%d"),
                    try:
                        birthday = birthday[0]
                    except:
                        birthday = profile_object.__dict__['birthday'].strftime("%Y-%m-%d")
                    diagnose = profile_object.__dict__['diagnose']
                    stage = profile_object.__dict__['stage']
                    dominantSide = profile_object.__dict__['dominantSide']
                    lded = profile_object.__dict__['lded']
                    ss = f'{target_account},{name},{gender},{birthday},{diagnose},{stage},{dominantSide},{lded},'
                
                orders = [
                    'stride length',
                    'stride width',
                    'stride time',
                    'velocity',
                    'cadence',
                    'turn time',
                ]

                request_objects = RequestModel.find_by_account(account=target_account)
                for request_object in request_objects:
                    sss = ss + f'{request_object.__dict__["date"].strftime("%Y-%m-%d")}'
                    result_objects = ResultModel.find_by_requestUUID(requestUUID=request_object.__dict__["submitUUID"])
                    collections = {
                        'stride length': 0,
                        'stride width': 0,
                        'stride time': 0,
                        'velocity': 0,
                        'cadence': 0,
                        'turn time': 0,
                    }
                    for result_object in result_objects:
                        result_key = result_object.__dict__['resultKey']
                        result_value = result_object.__dict__['resultValue']
                        if result_key in collections:
                            collections[result_key] = result_value
                    for order in orders:
                        sss += f',{collections[order]}'
                    sss += '\n'
                    csv += sss
        
        file_name = f'{generate_random_string(10)}_report.csv'
        with open(file_name, 'w') as f:
            f.write(csv)

        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_name)
            except Exception as error:
                current_app.logger.error("Error removing or closing downloaded file handle", error)
            return response

        return send_file(
            file_name,
            as_attachment=True,
            download_name='report.csv',
            mimetype='text/csv'
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