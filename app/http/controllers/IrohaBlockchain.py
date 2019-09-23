"""A IrohaBlockchain Module."""

import calendar
import json
import time

from masonite import env

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc

from iroha.primitive_pb2 import can_set_my_account_detail


class IrohaBlockchain:
    IROHA_HOST_ADDR = env("IROHA_HOST_ADDR", "127.0.0.1")
    IROHA_PORT = env("IROHA_PORT", "50051")

    def __init__(self, user_account, creator_private_key):
        self.user_account = user_account
        self.creator_private_key = creator_private_key
        self.iroha = Iroha(self.user_account)
        self.net = IrohaGrpc(f"{self.IROHA_HOST_ADDR}:{self.IROHA_PORT}")

    def send_transaction_and_return_status(self, transaction):
        """
        Sends a transaction to the blockchain
        """
        self.net.send_tx(transaction)
        stati = []

        for status in self.net.tx_status_stream(transaction):
            stati.append(status)

        return stati

    def create_account(self, user):
        """
        Creates a user account
        """
        txa = self.iroha.transaction(
            [
                self.iroha.command(
                    "CreateAccount",
                    account_name=user.gov_id,
                    domain_id="afyamkononi",
                    public_key=user.public_key,
                )
            ]
        )
        tx = IrohaCrypto.sign_transaction(txa, self.creator_private_key)
        return self.send_transaction_and_return_status(tx)

    def append_role(self, user):
        """
        Appends a role to a user
        """

        txa = self.iroha.transaction(
            [
                self.iroha.command(
                    "AppendRole",
                    account_id=f"{user.gov_id}@afyamkononi",
                    role_name=user.type,
                )
            ]
        )

        tx = IrohaCrypto.sign_transaction(txa, self.creator_private_key)
        return self.send_transaction_and_return_status(tx)

    def set_account_details(self, user):
        """
        Set account details
        """
        tx = self.iroha.transaction(
            [
                self.iroha.command(
                    "SetAccountDetail",
                    account_id=f"{user.gov_id}@afyamkononi",
                    key="gov_id",
                    value=f"{user.gov_id}",
                ),
                self.iroha.command(
                    "SetAccountDetail",
                    account_id=f"{user.gov_id}@afyamkononi",
                    key="name",
                    value=f"{user.name}",
                ),
                self.iroha.command(
                    "SetAccountDetail",
                    account_id=f"{user.gov_id}@afyamkononi",
                    key="email",
                    value=f"{user.email}",
                ),
                self.iroha.command(
                    "SetAccountDetail",
                    account_id=f"{user.gov_id}@afyamkononi",
                    key="phone_number",
                    value=f"{user.phone_number}",
                ),
            ]
        )

        IrohaCrypto.sign_transaction(tx, self.creator_private_key)
        return self.send_transaction_and_return_status(tx)

    def get_account_details(self, gov_id):
        """
        Get all the kv-storage entries for a user
        """

        query = self.iroha.query("GetAccountDetail", account_id=f"{gov_id}@afyamkononi")
        IrohaCrypto.sign_query(query, self.creator_private_key)

        response = self.net.send_query(query)
        return response.account_detail_response

    def grant_set_account_detail_perms(self, user):
        """
        Make creator account able to set detail to account
        """
        tx = self.iroha.transaction(
            [
                self.iroha.command(
                    "GrantPermission",
                    account_id=self.user_account,
                    permission=can_set_my_account_detail,
                )
            ],
            creator_account=f"{user.gov_id}@afyamkononi",
        )
        IrohaCrypto.sign_transaction(tx, user.private_key)
        return self.send_transaction_and_return_status(tx)

    def create_init_chain(self):
        iroha = Iroha("0000@afyamkononi")
        ad = "7ce6ab34236eaa4e21ee0acf93b04391091a66acb53332ac1efdb0d9745dd6ae"

        txb = iroha.transaction(
            [
                iroha.command(
                    "SetAccountDetail",
                    account_id="0000@afyamkononi",
                    key="gov_id",
                    value="0000",
                ),
                iroha.command(
                    "SetAccountDetail",
                    account_id="0000@afyamkononi",
                    key="name",
                    value="admin",
                ),
                iroha.command(
                    "SetAccountDetail",
                    account_id="0000@afyamkononi",
                    key="email",
                    value="admin@afyamkononi.com",
                ),
                iroha.command(
                    "SetAccountDetail",
                    account_id="0000@afyamkononi",
                    key="type",
                    value="admin",
                ),
                iroha.command(
                    "SetAccountDetail",
                    account_id="0000@afyamkononi",
                    key="phone_number",
                    value="0700000000",
                ),
            ]
        )
        tx = IrohaCrypto.sign_transaction(txb, ad)
        return self.send_transaction_and_return_status(tx)

    def set_patient_record(self, patient_id, patient_data):
        """
        Set patient records
        """
        timestamp_key = calendar.timegm(time.gmtime())
        patient_info = json.dumps(patient_data).replace('"', '\\"')
        txa = self.iroha.transaction(
            [
                self.iroha.command(
                    "SetAccountDetail",
                    account_id=f"{patient_id}@afyamkononi",
                    key=f"{timestamp_key}",
                    value=patient_info,
                )
            ]
        )

        tx = IrohaCrypto.sign_transaction(txa, self.creator_private_key)
        return self.send_transaction_and_return_status(tx)
