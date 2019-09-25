"""A PatientRecordsController Module."""
import ast
import calendar
import json
import jwt
import random
import re
import time
import app.http.controllers.utils as utils
from nested_lookup import nested_lookup

from app.User import User

from masonite.request import Request
from masonite.response import Response
from masonite.controllers import Controller
from masonite.validation import Validator

from app.http.controllers.IrohaBlockchain import IrohaBlockchain


class PatientRecordsController(Controller):
    """PatientRecordsController Controller Class."""

    def __init__(self, request: Request):
        """PatientRecordsController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request
        self.access_token = request.header("HTTP_AUTHORIZATION")

        if utils.validate_token(self.access_token) is True:
            token = re.sub("Bearer ", "", self.access_token)
            creator_info = utils.decode_token(token)
            if creator_info != False:
                self.creator_user = User.find(creator_info.get("id"))
                self.ibc = IrohaBlockchain(
                    f"{self.creator_user.gov_id}@afyamkononi",
                    self.creator_user.private_key,
                )
            else:
                self.ibc = IrohaBlockchain("0000@afyamkononi", "")
        else:
            self.ibc = IrohaBlockchain("0000@afyamkononi", "")

    def store(self, request: Request, response: Response, validate: Validator):
        if utils.validate_token(self.access_token) is not True:
            return response.json({"error": "Unauthorized access"})

        errors = request.validate(
            validate.required("symptoms"),
            validate.required("diagnosis"),
            validate.required("treatment_plan"),
        )

        if errors:
            return errors

        patient_id = request.param("patient_id")
        patient_record = {
            "timestamp": calendar.timegm(time.gmtime()),
            "symptoms": request.input("symptoms"),
            "diagnosis": request.input("diagnosis"),
            "treatment_plan": request.input("treatment_plan"),
        }

        patient_account = self.ibc.get_account_details(request.param("patient_id"))

        if patient_account.detail == "":
            return response.json({"error": "No such account"})

        unpacked_data = json.loads(patient_account.detail)

        patient_history = [
            inner
            for item in nested_lookup("medical_data", unpacked_data)
            for inner in ast.literal_eval(item)
        ]

        history_update = []
        if patient_history == []:
            history_update.append(patient_record)
        else:
            history_update += patient_history
            history_update.append(patient_record)

        history_update = self.remove_duplicates(history_update)

        update_status = self.ibc.set_patient_record(patient_id, history_update)

        if "STATEFUL_VALIDATION_FAILED" in update_status[1]:
            if update_status[1][2] is 1:
                return response.json({"error": "Could not set account detail"})
            if update_status[1][2] is 2:
                return response.json({"error": "No such permissions"})
            if update_status[1][2] is 3:
                return response.json({"error": "No such account"})

        return response.json({"success": "Medical data added successfully"})

    def remove_duplicates(self, duplicate):
        final_list = []
        for num in duplicate:
            if num not in final_list:
                final_list.append(num)
        return final_list

