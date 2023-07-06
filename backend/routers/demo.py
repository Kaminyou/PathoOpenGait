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
                'stride length': 109.7,
                'stride width': 23,
                'stride time': 1.1,
                'velocity': 1.4,
                'cadence': 0.8,
                'turn time': 1.2,
            },
            {
                'date': '2021-12-10',
                'dateUpload': '2021-12-10',
                'stride length': 108.5,
                'stride width': 21,
                'stride time': 1.2,
                'velocity': 1.5,
                'cadence': 0.9,
                'turn time': 1.1,
            },
            {
                'date': '2021-10-03',
                'dateUpload': '2021-10-03',
                'stride length': 112.4,
                'stride width': 23,
                'stride time': 1.1,
                'velocity': 1.4,
                'cadence': 0.8,
                'turn time': 1.2,
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
