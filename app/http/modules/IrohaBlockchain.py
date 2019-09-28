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

    def __init__(self):
        self.iroha = Iroha("0000@afyamkononi")
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

