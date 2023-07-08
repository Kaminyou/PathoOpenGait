from flask import Blueprint


demo_api = Blueprint('demo', __name__)


@demo_api.route('/profile/personal', methods=['GET'])
def demo_patient_info() -> dict:
    data = {
        'msg': 'success',
        'profile': {
            'name': 'anonymous',
            'birthday': '1980-03-15',
            'gender': 'female',
            'diagnose': 'PD',
            'stage': '2',
            'dominantSide': 'R',
            'lded': '350',
            'description': 'freezing',
        },
    }

    return data


@demo_api.route('/request/results', methods=['GET'])
def demo_gait_data() -> dict:
    data = {
        'msg': 'success',
        'results': [
            {
                'date': '2022-01-08',
                'dateUpload': '2022-01-08',
                'stride length': 109.74,
                'stride width': 23.11,
                'stride time': 1.12,
                'velocity': 1.43,
                'cadence': 0.81,
                'turn time': 1.23,
            },
            {
                'date': '2021-12-10',
                'dateUpload': '2021-12-10',
                'stride length': 108.54,
                'stride width': 21.20,
                'stride time': 1.23,
                'velocity': 1.58,
                'cadence': 0.99,
                'turn time': 1.17,
            },
            {
                'date': '2021-10-03',
                'dateUpload': '2021-10-03',
                'stride length': 112.46,
                'stride width': 23.84,
                'stride time': 1.12,
                'velocity': 1.44,
                'cadence': 0.85,
                'turn time': 1.29,
            },
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
            'velocity': 'Velocity (m/s)',
            'cadence': 'Cadence (1/min)',
            'turn_time': 'Turn time (s)',
        },
    }
    return data
