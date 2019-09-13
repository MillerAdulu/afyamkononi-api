"""A RegisterController Module."""

from masonite.request import Request
from masonite.view import View
from masonite.controllers import Controller
from app.User import User

from iroha import IrohaCrypto
import app.http.controllers.IrohaBlockchain as ibc

import json


class RegisterController(Controller):
    """RegisterController Controller Class."""

    def __init__(self, request: Request):
        """RegisterController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request

    def store(self, request: Request):
        priv_key = IrohaCrypto.private_key()
        pub_key = IrohaCrypto.derive_public_key(priv_key)

        user = User()

        user.name = request.input('name')
        user.email = request.input('email')
        user.password = request.input('password')
        user.type = request.input('type')
        user.private_key = priv_key
        user.public_key = pub_key

        user.save()

        block_status = ibc.create_account(user)
        if 'REJECTED' in block_status[2]:
            return {'error': 'REJECTED'}

        return user.to_json()
