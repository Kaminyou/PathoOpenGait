import os
from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from enums.request import Status
from inference.tasks import inference_gait_task
from models import ProfileModel, RequestModel, ResultModel, UserModel
from parsers.parser import parse_personal_profile, parse_request_instances
from schemas.profile import ProfileSchema
from schemas.request import RequestSchema
from security import get_sha256


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
        current_app.logger.info(f'trigger exception {e}')
        return (
            {'category': 'guest'},
            HTTPStatus.OK,
        )


# @user_api.route('/upload/gait', methods=['POST'])
# @jwt_required()
# def upload_gait_csv():
#     try:
#         account = get_jwt_identity()
#         user_instance = UserModel.find_by_account(account=account)

#         if user_instance is None:
#             return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

#         form_data = requestSchema.load(request.form)
#         form_data.update({"account": account})
#         request_obj = RequestModel(**form_data)

#         submit_uuid = request_obj.submitUUID

#         csv_file = request.files['csvFile']
#         mp4_file = request.files['mp4File']

#         data_root = f'data/{submit_uuid}'
#         os.makedirs(data_root)
#         os.makedirs(os.path.join(data_root, 'csv'))
#         os.makedirs(os.path.join(data_root, 'video'))
#         try:
#             csv_file.save(os.path.join(data_root, 'csv', 'uploaded.csv'))
#         except Exception:
#             current_app.logger.info(f'{account} submit with no 3D csv')
#         # csv_file.save(os.path.join(data_root, 'csv', 'uploaded.csv'))
#         mp4_file.save(os.path.join(data_root, 'video', 'uploaded.mp4'))
#         request_obj.save_to_db()
#         try:
#             task = inference_gait_task.delay(request_obj.submitUUID)
#             return (
#                 {
#                     'msg': 'File uploaded successfully',
#                     'task_id': task.id,
#                 },
#                 HTTPStatus.OK,
#             )

#         except Exception:
#             request_obj.delete_from_db()  # Rollback
#             return {'msg': 'Internal Server Error!'}, HTTPStatus.INTERNAL_SERVER_ERROR

#     except Exception as e:
#         current_app.logger.info(f'{account} trigger exception {e}')
#         return (
#             {'msg': 'Error'},
#             HTTPStatus.FORBIDDEN,
#         )

@user_api.route('/upload/gait', methods=['POST'])
@jwt_required()
def upload_gait_svo():
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        form_data = requestSchema.load(request.form)
        form_data.update({"account": account})
        trial_id = form_data['trialID']
        request_obj = RequestModel(**form_data)

        submit_uuid = request_obj.submitUUID

        svo_file = request.files['svoFile']
        txt_file = request.files['txtFile']

        data_root = f'data/{submit_uuid}'
        os.makedirs(data_root)
        os.makedirs(os.path.join(data_root, 'input'))
        try:
            svo_file.save(os.path.join(data_root, 'input', f'{trial_id}.svo'))
        except Exception as e:
            current_app.logger.info(f'{account} submit svo file fail due to {e}')
        try:
            txt_file.save(os.path.join(data_root, 'input', f'{trial_id}.txt'))
        except Exception as e:
            current_app.logger.info(f'{account} submit txt file fail due to {e}')
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


@user_api.route('/request/status', methods=['GET'])
@jwt_required()
def request_status():
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        request_objects = RequestModel.find_by_account(account=account)
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


@user_api.route('/request/results', methods=['GET'])
@jwt_required()
def request_results():
    try:
        account = get_jwt_identity()
        user_instance = UserModel.find_by_account(account=account)

        if user_instance is None:
            return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        request_objects = RequestModel.find_by_account_and_sort_by_exp_date(account=account)
        results = []
        for request_object in request_objects:
            if request_object.__dict__['status'] != Status.DONE:
                continue
            sub_results = {}
            sub_results['dateUpload'] = request_object.__dict__['dateUpload'].strftime("%Y-%m-%d")
            sub_results['date'] = request_object.__dict__['date'].strftime("%Y-%m-%d")
            sub_results['trialID'] = request_object.__dict__['trialID']
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


@user_api.route('/request/result', methods=['GET'])
# @jwt_required()
def request_result():
    try:
        # account = get_jwt_identity()
        # user_instance = UserModel.find_by_account(account=account)

        # if user_instance is None:
        #     return {'msg': 'User does not exist'}, HTTPStatus.FORBIDDEN

        submit_uuid = request.args.get('id')

        request_object = RequestModel.find_by_submitID(submitUUID=submit_uuid)

        sub_results = {}
        sub_results['upload date'] = request_object.__dict__['dateUpload'].strftime("%Y-%m-%d")
        sub_results['experiment date'] = request_object.__dict__['date'].strftime("%Y-%m-%d")
        sub_results['trial ID'] = request_object.__dict__['trialID']
        result_objects = ResultModel.find_by_requestUUID(requestUUID=submit_uuid)
        for result_object in result_objects:
            k = result_object.__dict__['resultKey']
            v = result_object.__dict__['resultValue']
            v_type = result_object.__dict__['resultType']
            if v_type == 'float':
                v = round(float(v), 2)
            sub_results[k] = v

        return (
            {
                'msg': 'success',
                'result': sub_results,
            },
            HTTPStatus.OK,
        )

    except Exception as e:
        current_app.logger.info(f'trigger exception {e}')
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
        current_app.logger.info(f'{account} trigger exception {e}')
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
            current_app.logger.info(f'{account} trigger exception {e}')
            return {"message": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR

    except Exception:
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR


@user_api.route('/profile/personal/uuid', methods=['GET'])
# @jwt_required()
def get_user_profile_with_uuid():
    try:
        # account = get_jwt_identity()
        # if not UserModel.find_by_account(account=account):
        #     return {"msg": "Wrong account or password"}, 401

        submit_uuid = request.args.get('id')
        request_object = RequestModel.find_by_submitID(submitUUID=submit_uuid)
        target_account = request_object.__dict__['account']

        profile_object = ProfileModel.find_latest_by_account(account=target_account)
        profile = parse_personal_profile(profile_object)
        try:
            return jsonify({"msg": "Submit successfully!", "profile": profile}), HTTPStatus.OK

        except Exception as e:
            current_app.logger.info(f'exception {e}')
            return {"message": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR

    except Exception:
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR


@user_api.route('/video', methods=['GET'])
# @jwt_required()
def get_video():
    try:
        # account = get_jwt_identity()
        # if not UserModel.find_by_account(account=account):
        #     return {"msg": "Wrong account or password"}, HTTPStatus.FORBIDDEN

        video_uuid = request.args.get('id')
        video_path = f'data/{video_uuid}/out/render.mp4'

        if os.path.exists(video_path):
            return send_file(video_path), HTTPStatus.OK

        else:
            return {"msg": "Internal Server Error!"}, HTTPStatus.FORBIDDEN
    except Exception:
        return {"msg": "Internal Server Error!"}, HTTPStatus.INTERNAL_SERVER_ERROR
