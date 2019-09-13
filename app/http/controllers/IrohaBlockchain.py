"""A IrohaBlockchain Module."""

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc

from iroha.primitive_pb2 import can_set_my_account_detail

import binascii
import os

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
IROHA_PORT = '50051'
ADMIN_ACCOUNT_ID = 'admin@test'
ADMIN_PRIVATE_KEY = os.getenv('ADMIN_PRIVATE_KEY',
                              'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))


def send_transaction_and_return_status(transaction):
    """
    Sends a transaction to the blockchain
    """
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))

    net.send_tx(transaction)
    stati = []

    for status in net.tx_status_stream(transaction):
        stati.append(status)

    return stati


def create_account(user):
    """
    Creates a user account
    """

    tx = iroha.transaction([
        iroha.command('CreateAccount', account_name=user.name,
                      domain_id='afyamkononi', public_key=user.public_key)
    ])

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    return send_transaction_and_return_status(tx)


def set_account_details(user):
    """
    Set account details
    """
    tx = iroha.transaction([
        iroha.command('SetAccountDetail',
                      account_id=f'{user.name}@afyamkononi', key='email',
                      value=f'{user.email}'),
        iroha.command('SetAccountDetail',
                      account_id=f'{user.name}@afyamkononi', key='name',
                      value=f'{user.name}'),
    ])

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    return send_transaction_and_return_status(tx)


def get_account_details(user):
    """
    Get all the kv-storage entries for a user
    """

    query = iroha.query('GetAccountDetail',
                        account_id=f'{user.name}@afyamkononi')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net.send_query(query)
    return response.account_detail_response


def grant_admin_set_account_detail_perms(account_name, priv_key):
    """
    Make admin@test able to set detail to account
    """
    tx = iroha.transaction([
        iroha.command('GrantPermission', account_id='admin@test',
                      permission=can_set_my_account_detail)
    ], creator_account=f'{account_name}@afyamkononi')
    IrohaCrypto.sign_transaction(tx, priv_key)
    return send_transaction_and_return_status(tx)
