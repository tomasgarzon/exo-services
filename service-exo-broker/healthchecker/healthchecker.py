import json

from local import EXOLEVER_HOST, SERVICES

import requests

TIMEOUT = 2


def application(env, start_response):
    """
    This is where uwsgi calls us.
    """
    def awesome(responses):
        headers = [('content-type', 'application/json')]
        text = json.dumps(responses)
        text1 = bytes(text, 'utf-8')
        start_response('200 OK', headers)
        return [text1]

    def notawesome():
        start_response('500', [])

    # These are the endpoints that we check to determine if we return
    # a 200 or a 500.
    responses = []
    status = 200
    for service_name in SERVICES:
        url = '{}{}/health/health/ping/'.format(
            EXOLEVER_HOST, service_name)
        try:
            response = requests.get(url, timeout=TIMEOUT)
            value = response.json()
        except Exception:
            responses.append([
                service_name,
                {
                    'url': url,
                    'status': 502,
                    'response': ''
                }
            ])
        else:
            responses.append([
                service_name,
                {
                    'url': url,
                    'status': response.status_code,
                    'response': value
                }
            ])
            if response.status_code != 200:
                status = response.status_code

    if status != 200:
        return notawesome()

    return awesome(responses)
