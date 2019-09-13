"""An AuthController Module."""

from masonite.request import Request
from masonite.view import View
from masonite.controllers import Controller
from app.User import User

from iroha import IrohaCrypto
import app.http.controllers.IrohaBlockchain as ibc

import json


class AuthController(Controller):
    """AuthController Controller Class."""

    def __init__(self, request: Request):
        """AuthController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request

    def register(self, request: Request):
        priv_key = IrohaCrypto.private_key()
        pub_key = IrohaCrypto.derive_public_key(priv_key)

        user = User()

        user.name = request.input('name')
        user.email = request.input('email')
        user.password = request.input('password')
        user.type = request.input('type')
        user.private_key = priv_key
        user.public_key = pub_key

        block_stati = ibc.create_account(user)

        if 'STATEFUL_VALIDATION_FAILED' in block_stati[1]:
            if block_stati[1][2] == 1:
                return {'error': 'Could not create account'}
            if block_stati[1][2] == 2:
                return {'error': 'No such permissions'}
            if block_stati[1][2] == 3:
                return {'error': 'No such domain'}
            if block_stati[1][2] == 4:
                return {'error': 'Account already exists'}

        block_stati = ibc.grant_admin_set_account_detail_perms(user.name,
                                                               priv_key)

        if 'STATEFUL_VALIDATION_FAILED' in block_stati[1]:
            if block_stati[1][2] == 1:
                return {'error': 'Could not grant permission'}
            if block_stati[1][2] == 2:
                return {'error': 'No such permissions'}
            if block_stati[1][2] == 3:
                return {'error': 'No such account'}

        block_stati = ibc.set_account_details(user)

        if 'STATEFUL_VALIDATION_FAILED' in block_stati[1]:
            if block_stati[1][2] == 1:
                return {'error': 'Could not set account detail'}
            if block_stati[1][2] == 2:
                return {'error': 'No such permissions'}
            if block_stati[1][2] == 3:
                return {'error': 'No such account'}

        user.save()
        return user.to_json()

    def view_user(self, request: Request):
        user = User.find(request.param('user'))

        data = ibc.get_account_details(user)

        return data.detail
