import datetime
import uuid
import random
import string


def get_uuid():
    return str(uuid.uuid4())


def get_AOETime(to_str=True):
    aoe_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=12))  # noqa
    if to_str:
        return aoe_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return aoe_time.replace(microsecond=0)


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))
