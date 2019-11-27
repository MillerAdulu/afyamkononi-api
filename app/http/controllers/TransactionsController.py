"""A TransactionsController Module."""

from masonite.request import Request
from masonite.response import Response
from masonite.controllers import Controller

from app.http.modules.IrohaBlockchain import IrohaBlockchain
from app.http.modules.utils import protobuf_to_dict

import app.http.modules.utils as utils


class TransactionsController(Controller):
    """TransactionsController Controller Class."""

    def __init__(self, request: Request):
        """TransactionsController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request
        self.user = request.user()
        self.ibc = IrohaBlockchain(self.user)

    def show(self, request: Request, response: Response):
        account_id = request.param("account_id")

        blockchain_data = self.ibc.get_all_account_transactions(account_id)
        blockchain_data = protobuf_to_dict(blockchain_data)
        blockchain_data = utils.format_transaction_data(blockchain_data)

        if blockchain_data is False:
            return response.json({"error": "No such permissions"})

        return response.json({"data": blockchain_data})

    def all_roles(self, response: Response):
        blockchain_data = self.ibc.get_all_roles()
        return response.json({"data": blockchain_data})

    def role_permissions(self, request: Request, response: Response):
        role_id = request.param("role")

        blockchain_data = self.ibc.get_role_permissions(role_id)
        blockchain_data = protobuf_to_dict(blockchain_data.role_permissions_response)

        return response.json({"data": blockchain_data})
