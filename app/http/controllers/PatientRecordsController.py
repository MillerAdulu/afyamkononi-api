"""A PatientRecordsController Module."""
import calendar
import json
import time

import app.http.modules.utils as utils
import app.http.modules.iroha_messages as iroha_messages

from app.User import User
from app.Consent import Consent

from masonite.request import Request
from masonite.response import Response
from masonite.controllers import Controller
from masonite.validation import Validator

from app.http.modules.IrohaBlockchain import IrohaBlockchain


class PatientRecordsController(Controller):
    """PatientRecordsController Controller Class."""

    def __init__(self, request: Request):
        """PatientRecordsController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request
        self.user = request.user()
        self.ibc = IrohaBlockchain(self.user)

    def index(self, response: Response):
        pass

    def store(self, request: Request, response: Response, validate: Validator):
        errors = request.validate(
            validate.required("symptoms"),
            validate.required("diagnosis"),
            validate.required("treatment_plan"),
            validate.required("seen_by"),
        )

        if errors:
            return errors

        patient_id = request.param("patient_id")
        patient_record = {
            "author": f"{self.user.gov_id}@afyamkononi",
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

        blockchain_status = self.ibc.set_patient_record(
            User.where("gov_id", patient_id).first(), history_update
        )
        print(blockchain_status)
        iroha_message = iroha_messages.update_medical_history_failed(blockchain_status)
        if iroha_message is not None:
            return response.json(iroha_message)

        return response.json({"success": "Medical data added successfully"})

    def show(self, request: Request, response: Response):
        """
        Retrieve medical records for a patient
        """

        subject = User.where("gov_id", request.param("patient_id")).first()
        if subject is None:
            return response.json({"error": "No such user"})

        requestor_id = f"{self.user.gov_id}@afyamkononi"
        grantor_id = f"{subject.gov_id}@afyamkononi"

        consent_confirm = (
            Consent.where("requestor_id", requestor_id)
            .where("grantor_id", grantor_id)
            .where("grantor_id", "!=", requestor_id)
            .first()
        )

        if consent_confirm is None and requestor_id != grantor_id:
            consent = Consent()
            consent.requestor_id = requestor_id
            consent.requestor_name = self.user.name
            consent.grantor_id = grantor_id
            consent.grantor_name = subject.name
            consent.permission = "can_set_my_account_detail"
            consent.save()
            return response.json(
                {
                    "error": "No such permissions. This owner has been requested to grant permissions."
                }
            )
        elif (
            consent_confirm is not None
            and consent_confirm.grantor_id != requestor_id
            and consent_confirm.status != "granted"
        ):
            consent_confirm.update(status="pending")
            return response.json(
                {
                    "error": "No such permissions. This owner has been requested to grant permissions."
                }
            )

        blockchain_data = self.ibc.get_account_details(subject.gov_id, "medical_data")
        if blockchain_data.detail == "":
            return response.json({"data": []})

        patient_medical_history = json.loads(blockchain_data.detail)
        filtered_patient_medical_history = utils.filter_medical_data(
            patient_medical_history
        )
        return response.json({"data": filtered_patient_medical_history})
