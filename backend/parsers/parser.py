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


def parse_personal_profile(
        profile_instance
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
