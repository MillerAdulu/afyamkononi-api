"""A PatientRecordsController Module."""
import calendar
import json
import jwt
import random
import re
import time

import app.http.controllers.utils as utils
import app.http.controllers.iroha_messages as iroha_messages

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
            "author": f"{self.creator_user.gov_id}@afyamkononi",
            "timestamp": calendar.timegm(time.gmtime()),
            "symptoms": request.input("symptoms"),
            "diagnosis": request.input("diagnosis"),
            "treatment_plan": request.input("treatment_plan"),
            "seen_by": request.input("seen_by"),
        }

        patient_account = self.ibc.get_account_details(request.param("patient_id"))

        if patient_account.detail == "":
            return response.json({"error": "No such account"})

        unpacked_data = json.loads(patient_account.detail)
        patient_history = utils.filter_medical_data(unpacked_data)

        history_update = []
        if patient_history == []:
            history_update.append(patient_record)
        else:
            history_update += patient_history
            history_update.append(patient_record)

        history_update = utils.remove_duplicates(history_update)

        blockchain_status = self.ibc.set_patient_record(patient_id, history_update)
        iroha_message = iroha_messages.update_medical_history_failed(blockchain_status)
        if iroha_message != None:
            return response.json(iroha_message)

        return response.json({"success": "Medical data added successfully"})

    def show(self, request: Request, response: Response):
        """
        Retrieve medical records for a patient
        """
        if utils.validate_token(self.access_token) is not True:
            return response.json({"error": "Unauthorized access"})

        patient_id = request.param("patient_id")
        blockchain_data = self.ibc.get_account_details(patient_id, "medical_data")
        if blockchain_data.detail == "":
            return response.json({"data": []})

        patient_medical_history = json.loads(blockchain_data.detail)
        filtered_patient_medical_history = utils.filter_medical_data(
            patient_medical_history
        )
        return response.json({"data": filtered_patient_medical_history})

