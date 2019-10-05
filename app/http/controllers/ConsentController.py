"""A ConsentController Module."""

from masonite.request import Request
from masonite.response import Response
from masonite.controllers import Controller

from app.Consent import Consent
import json


class ConsentController(Controller):
    """ConsentController Controller Class."""

    def __init__(self, request: Request):
        """ConsentController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request

    def show(self, request: Request, response: Response):
        gov_id = request.param("gov_id")

        consent_data = (
            Consent.where("grantor_id", f"{gov_id}@afyamkononi").get().to_json()
        )

        consent_data = json.loads(consent_data)

        return response.json({"data": consent_data})
