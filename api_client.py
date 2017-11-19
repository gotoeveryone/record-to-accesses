""" APIクライアント管理 """
import datetime
import hmac
import hashlib
import os
import sys
from urllib.parse import urlencode


def _sign(key, msg):
    """ return signed value """
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def _get_signature_key(key: str, amzdate: str, region: str, service: str):
    """ return signed signature """
    k_date = _sign(('AWS4' + key).encode('utf-8'), amzdate)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, service)
    k_signing = _sign(k_service, 'aws4_request')
    return k_signing


def _get_signed_headers(method: str, param_strings='', use_payload=False):
    """ APIクライアント取得 """
    # https://docs.aws.amazon.com/ja_jp/general/latest/gr/sigv4-signed-request-examples.html
    content_type = 'application/json'

    service = os.environ.get('AWS_API_SERVICE_NAME')
    host = os.environ.get('AWS_API_HOST')
    region = os.environ.get('AWS_API_REGION')

    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    if access_key is None or secret_key is None:
        print('No access key is available.')
        sys.exit()

    now = datetime.datetime.utcnow()
    amzdate = now.strftime('%Y%m%dT%H%M%SZ')
    datestamp = now.strftime('%Y%m%d')

    # ************* TASK 1: CREATE A CANONICAL REQUEST *************
    canonical_uri = '/social'
    canonical_querystring = '' if use_payload else param_strings
    canonical_headers = 'content-type:%s\nhost:%s\nx-amz-date:%s\n' % (
        content_type, host, amzdate)
    signed_headers = 'content-type;host;x-amz-date'
    payload_value = param_strings if use_payload else ''
    payload_hash = hashlib.sha256(payload_value.encode('utf-8')).hexdigest()
    canonical_request = '%s\n%s\n%s\n%s\n%s\n%s' % (method, canonical_uri, canonical_querystring,
                                                    canonical_headers, signed_headers, payload_hash)

    # ************* TASK 2: CREATE THE STRING TO SIGN*************
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = '%s/%s/%s/aws4_request' % (datestamp, region, service)
    string_to_sign = '%s\n%s\n%s\n%s' % (
        algorithm, amzdate, credential_scope,
        hashlib.sha256(canonical_request.encode('utf-8')).hexdigest())

    # ************* TASK 3: CALCULATE THE SIGNATURE *************
    signing_key = _get_signature_key(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode(
        'utf-8'), hashlib.sha256).hexdigest()

    # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
    authorization_header = '%s Credential=%s/%s, SignedHeaders=%s, Signature=%s' % (
        algorithm, access_key, credential_scope, signed_headers, signature)
    headers = {'Content-Type': content_type,
               'X-Amz-Date': amzdate,
               'Authorization': authorization_header}

    return headers


def get(endpoint: str, params=None):
    """ GETリクエスト """
    import requests
    param_strings = urlencode(params)
    headers = _get_signed_headers('GET', param_strings)
    return requests.get(endpoint, params=params, headers=headers)


def put(endpoint: str, data=None):
    """ PUTリクエスト """
    import json
    import requests
    request_data = json.dumps(data)
    headers = _get_signed_headers('PUT', request_data, use_payload=True)
    return requests.put(endpoint, data=request_data, headers=headers)
