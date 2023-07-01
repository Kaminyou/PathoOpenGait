from flask import Blueprint

demo_api = Blueprint('demo', __name__)


@demo_api.route('/patient/info', methods=['GET'])
def demo_patient_info() -> dict:
    data = {
        'msg': 'success',
        'data': {
            'name': 'anonymous',
            'birthday': '1980-03-15',
            'gender': 'female',
            'age': 43,
            'height': 166,
        },
    }

    return data


@demo_api.route('/patient/gait/data', methods=['GET'])
def demo_gait_data() -> dict:
    data = {
        'msg': 'success',
        'data': [
            {
                'date': '2021-10-03',
                'stride_length': 112.4,
                'stride_width': 23,
                'stride_time': 1.1,
                'velocity': 1.4,
                'cadence': 0.8,
                'turn_time': 1.2,
            },
            {
                'date': '2021-12-10',
                'stride_length': 108.5,
                'stride_width': 21,
                'stride_time': 1.2,
                'velocity': 1.5,
                'cadence': 0.9,
                'turn_time': 1.1,
            },
            {
                'date': '2022-01-08',
                'stride_length': 109.7,
                'stride_width': 23,
                'stride_time': 1.1,
                'velocity': 1.4,
                'cadence': 0.8,
                'turn_time': 1.2,
            }
        ]
    }
    return data


@demo_api.route('/patient/gait/unit', methods=['GET'])
def demo_gait_unit() -> dict:
    data = {
        'msg': 'success',
        'data': {
            'date': 'Date',
            'stride_length': 'Stride length (cm)',
            'stride_width': 'Stride width (cm)',
            'stride_time': 'Stride time (s)',
            'velocity': 'Velocity (m)',
            'cadence': 'Cadence (1/s)',
            'turn_time': 'Turn time (s)',
        },
    }
    return data
