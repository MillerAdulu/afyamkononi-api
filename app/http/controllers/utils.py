import ast
import re
import jwt

from nested_lookup import nested_lookup

from masonite import env

signing_key = env("JWT_KEY", "")
signing_alg = "HS256"


def validate_token(token):
    jwt = re.sub("Bearer ", "", token)
    return (
        token is not None
        and token != ""
        and jwt != ""
        and jwt != "null"
        and re.match(r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$", jwt)
        is not None
    )


def decode_token(token):
    try:
        info = jwt.decode(token, signing_key, algorithms=[signing_alg])
    except Exception:
        return False
    return info


def encode_message(message):
    try:
        token = jwt.encode(message, signing_key, algorithm=signing_alg)
    except Exception:
        return False
    return token


def remove_duplicates(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list


def filter_medical_data(blockchain_data):
    return [
        inner
        for item in nested_lookup("medical_data", blockchain_data)
        for inner in ast.literal_eval(item)
    ]
