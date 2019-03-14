from flask import request
from functools import wraps
from os import getenv
import jwt
from datetime import datetime

secret_key = getenv('SECRET_KEY')

authentication = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'x-client-token'
    }
}

referenceNumber = datetime.now().strftime("%Y%m%d%H%M%S")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-client-token' in request.headers:
            token = request.headers['x-client-token']
        if not token:
            return {'errors': {'statusCode': 401,
                               'errorCode': 'A001',
                               'message': 'Unauthorized'}}, 401
        try:
            jwt.decode(token, secret_key)
        except jwt.exceptions.ExpiredSignatureError:
            return {'errors': {'statusCode': 401,
                               'errorCode': 'A002',
                               'message': 'Expired Token'}}, 401
        except jwt.exceptions.InvalidTokenError:
            return {'errors': {'statusCode': 401,
                               'errorCode': 'A003',
                               'message': 'Invalid Token'}}, 401
        return f(*args, **kwargs)
    return decorated

def token_details(token):
    try:
        decoded = jwt.decode(token, secret_key)
        return decoded
    except jwt.exceptions.ExpiredSignatureError:
            return {'errors': {'statusCode': 401,
                               'errorCode': 'A002',
                               'message': 'Expired Token'}}, 401
    except jwt.exceptions.InvalidTokenError:
        return {'errors': {'statusCode': 401,
                           'errorCode': 'A003',
                           'message': 'Invalid Token'}}, 401