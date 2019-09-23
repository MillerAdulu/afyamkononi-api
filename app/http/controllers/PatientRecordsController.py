"""A PatientRecordsController Module."""
import json
import jwt
import random
import re
import app.http.controllers.utils as utils

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

        account = self.ibc.get_account_details(request.param("patient_id"))
        if account.detail == "":
            return response.json({"error": "No such account"})

        patient_id = request.param("patient_id")
        patient_data = {
            "symptoms": request.input("symptoms"),
            "diagnosis": request.input("diagnosis"),
            "treatment_plan": request.input("treatment_plan"),
        }

        update_status = self.ibc.set_patient_record(patient_id, patient_data)

        if "STATEFUL_VALIDATION_FAILED" in update_status[1]:
            if update_status[1][2] is 1:
                return response.json({"error": "Could not set account detail"})
            if update_status[1][2] is 2:
                return response.json({"error": "No such permissions"})
            if update_status[1][2] is 3:
                return response.json({"error": "No such account"})

        return response.json({"success": "Medical data added successfully"})
