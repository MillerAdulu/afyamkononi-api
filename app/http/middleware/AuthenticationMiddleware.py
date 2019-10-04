"""Authentication Middleware."""

import re

from masonite.request import Request
from masonite.response import Response

import app.http.modules.utils as utils
from app.http.modules.IrohaBlockchain import IrohaBlockchain
from app.User import User


class AuthenticationMiddleware:
    """Middleware To Check If The User Is Logged In."""

    def __init__(self, request: Request, response: Response):
        """Inject Any Dependencies From The Service Container.

        Arguments:
            request {masonite.request.Request} -- The Masonite request class.
        """
        self.request = request
        self.response = response

    def before(self):
        """Run This Middleware Before The Route Executes."""
        access_token = self.request.header("HTTP_AUTHORIZATION")

        if utils.validate_token(access_token) is True:
            token = re.sub("Bearer ", "", access_token)
            creator_info = utils.decode_token(token)
            if creator_info != False:
                creator_user = User.find(creator_info.get("id"))
                self.request.set_user(creator_user)
            else:
                self.response.json({"error": "Unauthorized access"})
                
        if utils.validate_token(access_token) is not True:
            self.response.json({"error": "Unauthorized access"})

    def after(self):
        """Run This Middleware After The Route Executes."""
        pass
