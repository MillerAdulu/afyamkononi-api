"""An AuthController Module."""

import json
import jwt
import random
import re
import app.http.controllers.utils as utils

from app.User import User
from app.http.controllers.IrohaBlockchain import IrohaBlockchain

from masonite import env

from masonite.request import Request
from masonite.response import Response
from masonite.view import View
from masonite.controllers import Controller
from masonite.auth import Auth

from iroha import IrohaCrypto

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class AuthController(Controller):
    """AuthController Controller Class."""

    def __init__(self, request: Request):
        """AuthController Initializer

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

    def register(self, request: Request, response: Response, auth: Auth):

        if utils.validate_token(self.access_token) is not True:
            return response.json({"error": "Unauthorized access"})

        priv_key = IrohaCrypto.private_key()
        pub_key = IrohaCrypto.derive_public_key(priv_key)

        user = User()
        user.name = request.input("name")
        user.email = request.input("email")
        user.type = request.input("type")
        user.gov_id = request.input("gov_id")
        user.phone_number = request.input("phone_number")
        user.private_key = priv_key.decode("utf-8")
        user.public_key = pub_key.decode("utf-8")
        if user.type == "user":
            user.password = str(random.randrange(1000, 9999))
        else:
            user.password = request.input("password")

        block_stati = self.ibc.create_account(user)

        if "STATEFUL_VALIDATION_FAILED" in block_stati[1]:
            if block_stati[1][2] is 1:
                return response.json({"error": "Could not create account"})
            if block_stati[1][2] is 2:
                return response.json({"error": "No such permissions"})
            if block_stati[1][2] is 3:
                return response.json({"error": "No such domain"})
            if block_stati[1][2] is 4:
                return response.json({"error": "Account already exists"})

        block_stati = self.ibc.grant_set_account_detail_perms(
            user, self.creator_user.gov_id
        )

        if "STATEFUL_VALIDATION_FAILED" in block_stati[1]:
            if block_stati[1][2] is 1:
                return response.json({"error": "Could not grant permission"})
            if block_stati[1][2] is 2:
                return response.json({"error": "No such permissions"})
            if block_stati[1][2] is 3:
                return response.json({"error": "No such account"})

        block_stati = self.ibc.set_account_details(user)

        if "STATEFUL_VALIDATION_FAILED" in block_stati[1]:
            if block_stati[1][2] is 1:
                return response.json({"error": "Could not set account detail"})
            if block_stati[1][2] is 2:
                return response.json({"error": "No such permissions"})
            if block_stati[1][2] is 3:
                return response.json({"error": "No such account"})

        if user.type != "user":
            block_stati = self.ibc.append_role(user)

            if "STATEFUL_VALIDATION_FAILED" in block_stati[1]:
                if block_stati[1][2] is 1:
                    return response.json({"error": "Could not append role"})
                if block_stati[1][2] is 2:
                    return response.json({"error": "No such permissions"})
                if block_stati[1][2] is 3:
                    return response.json({"error": "No such account"})
                if block_stati[1][2] is 4:
                    return response.json({"error": "No such role"})

        res = auth.register(
            {
                "name": user.name,
                "email": user.email,
                "password": user.password,
                "type": user.type,
                "private_key": user.private_key,
                "public_key": user.public_key,
                "gov_id": user.gov_id,
                "phone_number": user.phone_number,
            }
        )

        if res is None and user.type == "user":
            message = Mail(
                from_email=env("MAIL_FROM_ADDRESS", ""),
                to_emails=user.email,
                subject="Afya Mkononi Auth Details",
                html_content=f"<div> <p>Welcome to this cool health service</p> <p>Your email: { user.email }</p> <p>Your Password: { user.password }</p>",
            )

            sg = SendGridAPIClient(env("SENDGRID_KEY"))
            sg.send(message)
            return response.json({"success": "Check your email for your credentials"})

        elif res is None:
            return response.json({"success": "Account has been added"})

        return response.json({"error": "Failed to add account"})

    def view_user(self, request: Request, response: Response):
        if utils.validate_token(self.access_token) is not True:
            return response.json({"error": "Unauthorized access"})

        user = User.find(request.param("user"))
        if user is None:
            return response.json({"error": "No such user"})
        data = self.ibc.get_account_details(user.gov_id)

        return data.detail

    def sign_in(self, request: Request, response: Response, auth: Auth):
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
        self.ibc.create_init_chain()
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

