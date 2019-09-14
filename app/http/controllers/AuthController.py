"""An AuthController Module."""

import json
import os
import jwt

from masonite.request import Request
from masonite.response import Response
from masonite.view import View
from masonite.controllers import Controller
from masonite.auth import Auth
from app.User import User

from iroha import IrohaCrypto

from app.http.controllers.IrohaBlockchain import IrohaBlockchain


class AuthController(Controller):
    """AuthController Controller Class."""

    def __init__(self, request: Request):
        """AuthController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request
        self.ibc = IrohaBlockchain('admin@test',
                                   'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

    def register(self, request: Request, response: Response, auth: Auth):
        priv_key = IrohaCrypto.private_key()
        pub_key = IrohaCrypto.derive_public_key(priv_key)

        user = User()

        user.name = request.input('name')
        user.email = request.input('email')
        user.password = request.input('password')
        user.type = request.input('type')
        user.private_key = priv_key
        user.public_key = pub_key

        block_stati = self.ibc.create_account(user)

        if 'STATEFUL_VALIDATION_FAILED' in block_stati[1]:
            if block_stati[1][2] == 1:
                return response.json({'error': 'Could not create account'})
            if block_stati[1][2] == 2:
                return response.json({'error': 'No such permissions'})
            if block_stati[1][2] == 3:
                return response.json({'error': 'No such domain'})
            if block_stati[1][2] == 4:
                return response.json({'error': 'Account already exists'})

        block_stati = self.ibc.grant_admin_set_account_detail_perms(user.name,
                                                               priv_key)

        if 'STATEFUL_VALIDATION_FAILED' in block_stati[1]:
            if block_stati[1][2] == 1:
                return response.json({'error': 'Could not grant permission'})
            if block_stati[1][2] == 2:
                return response.json({'error': 'No such permissions'})
            if block_stati[1][2] == 3:
                return response.json({'error': 'No such account'})

        block_stati = self.ibc.set_account_details(user)

        if 'STATEFUL_VALIDATION_FAILED' in block_stati[1]:
            if block_stati[1][2] == 1:
                return response.json({'error': 'Could not set account detail'})
            if block_stati[1][2] == 2:
                return response.json({'error': 'No such permissions'})
            if block_stati[1][2] == 3:
                return response.json({'error': 'No such account'})

        res = auth.register({
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "type": user.type,
            "private_key": user.private_key,
            "public_key": user.public_key
        })

        if res is None:
            return response.json({'success': 'User has been added'})

        return response.json({'error': 'Failed to add user'})

    def view_user(self, request: Request, response: Response):
        user = User.find(request.param('user'))
        if user is None:
            return response.json({'error': 'No such user'})
        data = self.ibc.get_account_details(user)

        return data.detail

    def sign_in(self, request: Request, response: Response, auth: Auth):
        user_auth_res = auth.login(
            request.input('email'),
            request.input('password')
        )

        if user_auth_res is False:
            return response.json({'error': 'Check your credentials'})
        msg = {
            'id': user_auth_res.id,
            'email': user_auth_res.email,
            'name': user_auth_res.name,
            'type': user_auth_res.type
        }
        signing_key = os.getenv('JWT_KEY', '')
        enc = jwt.encode(msg, signing_key, algorithm='HS256')
        
        return response.json({'access_token': enc.decode('utf-8')})
