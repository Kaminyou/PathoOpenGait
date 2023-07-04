import time
from datetime import datetime


PERSON_PROFILE_KEY = {
    'name': str,
    'gender': str,
    'birthday': lambda x: x.strftime("%Y-%m-%d"),
    'diagnose': str,
    'stage': str,
    'dominantSide': str,
    'lded': str,
    'description': str,
}


REQUEST_STATUS_KEY = {
    'dateUpload': lambda x: x.strftime("%Y-%m-%d"),
    'date': lambda x: x.strftime("%Y-%m-%d"),
    'description': str,
    'status': lambda x: x.name,
}



def parse_personal_profile(
    profile_instance,
):
    response = {}
    for k, v in profile_instance.__dict__.items():
        try:
            if k in PERSON_PROFILE_KEY:
                if v is None:
                    v = ''
                else:
                    transform = PERSON_PROFILE_KEY[k]
                    v = transform(v)
                response[k] = v
        except:
            pass
    return response


def parse_request_instance(
    request_instance,
):
    response = {}
    for k, v in request_instance.__dict__.items():
        try:
            if k in REQUEST_STATUS_KEY:
                if v is None:
                    v = ''
                else:
                    transform = REQUEST_STATUS_KEY[k]
                    v = transform(v)
                response[k] = v
        except:
            pass
    return response


def parse_request_instances(request_instances):
    results = []
    for request_instance in request_instances:
        results.append(parse_request_instance(request_instance))
    return results
