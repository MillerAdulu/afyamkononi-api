def create_account_failed(blockchain_status):
    if "STATEFUL_VALIDATION_FAILED" in blockchain_status[1]:
        if blockchain_status[1][2] is 1:
            return {"error": "Could not create account"}
        if blockchain_status[1][2] is 2:
            return {"error": "No such permissions"}
        if blockchain_status[1][2] is 3:
            return {"error": "No such domain"}
        if blockchain_status[1][2] is 4:
            return {"error": "Account already exists"}
    return None


def grant_set_account_detail_perms_failed(blockchain_status):
    if "STATEFUL_VALIDATION_FAILED" in blockchain_status[1]:
        if blockchain_status[1][2] is 1:
            return {"error": "Could not grant permission"}
        if blockchain_status[1][2] is 2:
            return {"error": "No such permissions"}
        if blockchain_status[1][2] is 3:
            return {"error": "No such account"}
    return None

def revoke_set_account_detail_perms_failed(blockchain_status):
    if "STATEFUL_VALIDATION_FAILED" in blockchain_status[1]:
        if blockchain_status[1][2] is 1:
            return {"error": "Could not revoke permission"}
        if blockchain_status[1][2] is 2:
            return {"error": "No such permissions"}
        if blockchain_status[1][2] is 3:
            return {"error": "No such account"}
    return None


def set_account_details_failed(blockchain_status):
    if "STATEFUL_VALIDATION_FAILED" in blockchain_status[1]:
        if blockchain_status[1][2] is 1:
            return {"error": "Could not set account detail"}
        if blockchain_status[1][2] is 2:
            return {"error": "No such permissions"}
        if blockchain_status[1][2] is 3:
            return {"error": "No such account"}
    return None


def append_role_failed(blockchain_status):
    if "STATEFUL_VALIDATION_FAILED" in blockchain_status[1]:
        if blockchain_status[1][2] is 1:
            return {"error": "Could not append role"}
        if blockchain_status[1][2] is 2:
            return {"error": "No such permissions"}
        if blockchain_status[1][2] is 3:
            return {"error": "No such account"}
        if blockchain_status[1][2] is 4:
            return {"error": "No such role"}
    return None


def update_medical_history_failed(blockchain_status):
    if "STATEFUL_VALIDATION_FAILED" in blockchain_status[1]:
        if blockchain_status[1][2] is 1:
            return {"error": "Could not set account detail"}
        if blockchain_status[1][2] is 2:
            return {"error": "No such permissions"}
        if blockchain_status[1][2] is 3:
            return {"error": "No such account"}
    return None
