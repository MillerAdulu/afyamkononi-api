"""A IrohaBlockchain Module."""

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc

from iroha.primitive_pb2 import can_set_my_account_detail

import binascii

IROHA_HOST_ADDR = '127.0.0.1'
IROHA_PORT = '50051'
ADMIN_ACCOUNT_ID = 'admin@test'
ADMIN_PRIVATE_KEY = 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70'

user_private_key = IrohaCrypto.private_key()
user_public_key = IrohaCrypto.derive_public_key(user_private_key)

iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))


def run():
    create_domain()
    # create_account()
    # kmpdu_grants_to_admin_set_account_detail_permisson()
    # set_name_to_kmpdu()
    # get_kmpdu_details()
    print('Done')


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


def create_domain():
    """
    Creates domain 'domain'
    """

    command = [
        iroha.command('CreateDomain', domain_id='afyamkononi',
                      default_role='user')
        ]

    tx = IrohaCrypto.sign_transaction(iroha.transaction(command),
                                      ADMIN_PRIVATE_KEY)

    send_transaction_and_return_status(tx)


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


def kmpdu_grants_to_admin_set_account_detail_permisson():
    """
    Make admin@test able to set detail to kmpdu
    """
    tx = iroha.transaction([
        iroha.command('GrantPermission', account_id='admin@test',
                      permission=can_set_my_account_detail)
    ], creator_account='kmpdu@afyamkononi')
    IrohaCrypto.sign_transaction(tx, user_private_key)
    send_transaction_and_return_status(tx)


def set_name_to_kmpdu():
    """
    Set name to kmpdu@afyamkononi.com by admin@test
    """
    tx = iroha.transaction([
        iroha.command('SetAccountDetail', account_id='kmpdu@afyamkononi',
                      key='name', value='wozzap'),
        iroha.command('SetAccountDetail', account_id='kmpdu@afyamkononi',
                      key='zamzing', value='zamzam')
    ])

    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_return_status(tx)


def get_kmpdu_details():
    """
    Get all the kv-storage entries for kmpdu@afyamkononi
    """

    query = iroha.query('GetAccountDetail', account_id='kmpdu@afyamkononi')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net.send_query(query)
    data = response.account_detail_response
    print('Account id = {}, details = {}'.format('kmpdu@afyamkononi',
                                                 data.detail))
