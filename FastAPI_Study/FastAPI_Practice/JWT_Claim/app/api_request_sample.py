import base64
import hmac
from datetime import datetime, timedelta

import requests


def parse_params_to_str(params):
    url = "?"
    for key, value in params.items():
        url = url + str(key) + "=" + str(value) + "&"
    return url[1:-1]


def hash_string(qs, secret_key):
    mac = hmac.new(bytes(secret_key, encoding='utf-8'),
                   bytes(qs, encoding='utf8'), digestmod='sha256')
    d = mac.digest()
    validating_secret = str(base64.b64encode(d).decode('utf-8'))
    return validating_secret


def sample_request():
    access_key = "3de14228-e1b0-4858-9515-95d137cf-e9bf-4409-8105-6a074c131db7"
    secret_key = "3kAIBXmhCJ5k3XVLSYcaAS45m2uUCW5gIWkiw8Pl"
    cur_time = datetime.utcnow()+timedelta(hours=9)
    cur_timestamp = int(cur_time.timestamp())
    qs = dict(key=access_key, timestamp=cur_timestamp)
    header_secret = hash_string(parse_params_to_str(qs), secret_key)

    url = f"http://127.0.0.1:8000/api/services?{parse_params_to_str(qs)}"
    res = requests.get(url, headers=dict(secret=header_secret))
    return res


print(sample_request().json())
