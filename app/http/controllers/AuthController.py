"""A AuthController Module."""

import app.http.modules.utils as utils

from masonite.request import Request
from masonite.response import Response
from masonite.controllers import Controller
from masonite.auth import Auth
from masonite.validation import Validator


class AuthController(Controller):
    """AuthController Controller Class."""

    def __init__(self, request: Request):
        """AuthController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request

    def sign_in(
        self, request: Request, response: Response, auth: Auth, validate: Validator
    ):

        errors = request.validate(
            validate.required("email"), validate.required("password")
        )

        if errors:
            return errors

        user_auth_res = auth.login(request.input("email"), request.input("password"))

        if user_auth_res is False:
            return response.json({"error": "Check your credentials"})

        msg = {
            "id": user_auth_res.id,
            "email": user_auth_res.email,
            "name": user_auth_res.name,
            "type": user_auth_res.type,
        }

        enc = utils.encode_message(msg)
        if enc != False:
            return response.json({"access_token": enc.decode("utf-8")})

        return response.json({"error": "You cannot access this system at the time"})

    def seed_admin(self, request: Request, response: Response, auth: Auth):
        # self.ibc.create_init_chain()
        res = auth.register(
            {
                "name": request.input("name"),
                "email": request.input("email"),
                "password": request.input("password"),
                "type": request.input("type"),
                "private_key": "7ce6ab34236eaa4e21ee0acf93b04391091a66acb53332ac1efdb0d9745dd6ae",
                "public_key": "06599fc060d23cfb25f88235311e139243b83f3c57bb1e4fc8926eba34a82dbd",
                "gov_id": request.input("gov_id"),
                "phone_number": request.input("phone_number"),
            }
        )

        if res is None:
            return response.json({"success": "User has been added"})

        return response.json({"error": "Failed to add user"})
