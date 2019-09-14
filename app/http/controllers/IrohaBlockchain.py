"""A IrohaBlockchain Module."""

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc

from iroha.primitive_pb2 import can_set_my_account_detail

import os


class IrohaBlockchain:
    IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
    IROHA_PORT = os.getenv('IROHA_PORT', '50051')
    
    def __init__(self, user_account_id, user_private_key):
        if os.environ.get('https_proxy'):
            del os.environ['https_proxy']   
        if os.environ.get('http_proxy'):
            del os.environ['http_proxy']
        self.user_account = user_account_id
        self.ADMIN_PRIVATE_KEY = user_private_key
        self.iroha = Iroha(self.user_account)
        self.net = IrohaGrpc(f'{self.IROHA_HOST_ADDR}:{self.IROHA_PORT}')

    def send_transaction_and_return_status(self, transaction):
        """
        Sends a transaction to the blockchain
        """
        self.net.send_tx(transaction)
        stati = []

        for status in net.tx_status_stream(transaction):
            stati.append(status)

        return stati

    def create_account(self, user):
        """
        Creates a user account
        """

        tx = self.iroha.transaction([
            self.iroha.command('CreateAccount', account_name=user.name,
                          domain_id='afyamkononi', public_key=user.public_key)
        ])

        IrohaCrypto.sign_transaction(tx, self.ADMIN_PRIVATE_KEY)
        return self.send_transaction_and_return_status(tx)

    def set_account_details(self, user):
        """
        Set account details
        """
        tx = self.iroha.transaction([
            self.iroha.command('SetAccountDetail',
                          account_id=f'{user.name}@afyamkononi', key='email',
                          value=f'{user.email}'),
            self.iroha.command('SetAccountDetail',
                          account_id=f'{user.name}@afyamkononi', key='name',
                          value=f'{user.name}'),
        ])

        IrohaCrypto.sign_transaction(tx, self.ADMIN_PRIVATE_KEY)
        return self.send_transaction_and_return_status(tx)

    def get_account_details(self, user):
        """
        Get all the kv-storage entries for a user
        """

        query = self.iroha.query('GetAccountDetail',
                            account_id=f'{user.name}@afyamkononi')
        IrohaCrypto.sign_query(query, self.ADMIN_PRIVATE_KEY)

        response = self.net.send_query(query)
        return response.account_detail_response

    def grant_admin_set_account_detail_perms(self, account_name, priv_key):
        """
        Make admin@test able to set detail to account
        """
        tx = self.iroha.transaction([
            self.iroha.command('GrantPermission', account_id='admin@test',
                          permission=can_set_my_account_detail)
        ], creator_account=f'{account_name}@afyamkononi')
        IrohaCrypto.sign_transaction(tx, priv_key)
        return self.send_transaction_and_return_status(tx)
