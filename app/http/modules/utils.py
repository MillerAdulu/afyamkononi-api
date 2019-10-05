import ast
import json
import jwt
import re

from nested_lookup import nested_lookup
from protobuf_to_dict import protobuf_to_dict

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


def format_query_result(blockchain_data):
    data = json.loads(blockchain_data.detail)
    medical_data = filter_medical_data(data)

    data = sum(data.items(), ())

    medical_data = remove_duplicates(medical_data)

    if medical_data == []:
        return {"creator": data[0], "data": data[1]}
    else:
        return {
            "creator": data[0],
            "data": {
                "name": data[1]["name"],
                "email": data[1]["email"],
                "gov_id": data[1]["gov_id"],
                "phone_number": data[1]["phone_number"],
                "medical_data": medical_data,
            },
        }


def format_transaction_data(blockchain_data):
    if "error_response" in blockchain_data.keys():
        return False

    transactions = blockchain_data["transactions_page_response"]["transactions"]
    transactions = filter_payload(transactions)

    return {
        "query_hash": blockchain_data["query_hash"],
        "transactions_page_response": {
            "all_transactions_size": blockchain_data["transactions_page_response"][
                "all_transactions_size"
            ],
            "transactions": transactions,
        },
    }


def filter_payload(transaction_payloads):
    final_commands = []
    for payload in transaction_payloads:
        all_commands = filter_commands(payload)

        for tx in all_commands:
            in_list = sum(tx.items(), ())
            final_commands.append(
                {
                    "action": in_list[0],
                    "data": in_list[1],
                    "creator_account_id": payload["payload"]["reduced_payload"][
                        "creator_account_id"
                    ],
                    "created_time": payload["payload"]["reduced_payload"][
                        "created_time"
                    ],
                    "quorum": payload["payload"]["reduced_payload"]["quorum"],
                    "signatures": payload["signatures"],
                }
            )

    return final_commands


def filter_commands(transaction_payload):
    commands = nested_lookup("commands", transaction_payload)
    all_commands = []
    for command in commands:
        all_commands += command
    return all_commands
