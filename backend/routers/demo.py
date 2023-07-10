from flask import Blueprint


demo_api = Blueprint('demo', __name__)


@demo_api.route('/profile/personal', methods=['GET'])
def demo_patient_info() -> dict:
    data = {
        'msg': 'success',
        'profile': {
            'name': 'Ming-Yang Ho',
            'birthday': '1996-02-17',
            'gender': 'M',
            'diagnose': 'HC',
            'stage': 'NA',
            'dominantSide': 'NA',
            'lded': 'NA',
            'description': 'NA',
        },
    }

    return data


@demo_api.route('/request/results', methods=['GET'])
def demo_gait_data() -> dict:
    data = {
        'msg': 'success',
        'results': [
            {
                'date': '2023-03-08',
                'dateUpload': '2023-07-09',
                'stride length': 191.98,
                'stride width': 15.56,
                'stride time': 0.98,
                'velocity': 1.96,
                'cadence': 61.29,
                'turn time': 1.26,
                'detail': '90720458-00c7-44af-98ef-30863fe998ef',
            },
            {
                'date': '2023-03-07',
                'dateUpload': '2023-07-09',
                'stride length': 184.92,
                'stride width': 13.05,
                'stride time': 1.05,
                'velocity': 1.76,
                'cadence': 57.12,
                'turn time': 1.23,
                'detail': 'ea074574-0d8b-49b4-a8f1-8bdb3b5776c1',
            },
            {
                'date': '2023-03-06',
                'dateUpload': '2023-07-09',
                'stride length': 185.33,
                'stride width': 12.84,
                'stride time': 1.01,
                'velocity': 1.83,
                'cadence': 59.38,
                'turn time': 1.32,
                'detail': 'b38a8094-9df6-441d-80eb-bd0a1ee439cc',
            },
            {
                'date': '2023-03-05',
                'dateUpload': '2023-07-09',
                'stride length': 212.93,
                'stride width': 21.54,
                'stride time': 1.03,
                'velocity': 2.07,
                'cadence': 58.24,
                'turn time': 1.14,
                'detail': '3f74ae18-826f-47aa-970a-ecb2368e5605',
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
