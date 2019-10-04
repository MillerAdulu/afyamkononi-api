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
