"""An AccountController Module."""

import random

import app.http.modules.utils as utils
import app.http.modules.iroha_messages as iroha_messages

from app.User import User
from app.Consent import Consent
from app.http.modules.IrohaBlockchain import IrohaBlockchain

from masonite import env

from masonite.request import Request
from masonite.response import Response
from masonite.controllers import Controller
from masonite.auth import Auth

from masonite.validation import Validator

from iroha import IrohaCrypto

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class AccountController(Controller):
    """AuthController Controller Class."""

    def __init__(self, request: Request):
        """AccountController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request
        self.user = request.user()
        self.ibc = IrohaBlockchain(self.user)

    def register(
        self, request: Request, response: Response, auth: Auth, validate: Validator
    ):

        errors = request.validate(
            validate.required("name"),
            validate.required("email"),
            validate.required("type"),
            validate.required("gov_id"),
            validate.required("phone_number"),
        )

        if errors:
            return errors

        priv_key = IrohaCrypto.private_key()
        pub_key = IrohaCrypto.derive_public_key(priv_key)

        user = User()
        user.name = request.input("name")
        user.email = request.input("email")
        user.type = request.input("type")
        user.gov_id = request.input("gov_id")
        user.phone_number = request.input("phone_number")
        user.private_key = priv_key.decode("utf-8")
        user.public_key = pub_key.decode("utf-8")
        if user.type == "user":
            user.password = str(random.randrange(1000, 9999))
        else:
            user.password = request.input("password")

        blockchain_status = self.ibc.create_account(user)
        iroha_message = iroha_messages.create_account_failed(blockchain_status)
        if iroha_message != None:
            return response.json(iroha_message)

        blockchain_status = self.ibc.grant_set_account_detail_perms(user)
        iroha_message = iroha_messages.grant_set_account_detail_perms_failed(
            blockchain_status
        )
        if iroha_message != None:
            return response.json(iroha_message)

        blockchain_status = self.ibc.set_account_details(user)
        iroha_message = iroha_messages.set_account_details_failed(blockchain_status)
        if iroha_message != None:
            return response.json(iroha_message)

        if user.type != "user":
            blockchain_status = self.ibc.append_role(user)
            iroha_message = iroha_messages.append_role_failed(blockchain_status)
            if iroha_message != None:
                return response.json(iroha_message)

        if user.type == "user":
            blockchain_status = self.ibc.revoke_set_account_detail_perms(user)
            iroha_message = iroha_messages.revoke_set_account_detail_perms_failed(
                blockchain_status
            )
            if iroha_message != None:
                return response.json(iroha_message)

        res = auth.register(
            {
                "name": user.name,
                "email": user.email,
                "password": user.password,
                "type": user.type,
                "private_key": user.private_key,
                "public_key": user.public_key,
                "gov_id": user.gov_id,
                "phone_number": user.phone_number,
            }
        )

        if res is None and user.type == "user":
            message = Mail(
                from_email=env("MAIL_FROM_ADDRESS"),
                to_emails=user.email,
                subject="Afya Mkononi Auth Details",
                html_content=f"<div> <p>Welcome to this cool health service</p> <p>Your email: { user.email }</p> <p>Your Password: { user.password }</p>",
            )

            sg = SendGridAPIClient(env("SENDGRID_KEY"))
            sg.send(message)
            return response.json({"success": "Check your email for your credentials"})

        elif res is None:
            return response.json({"success": "Account has been added"})

        return response.json({"error": "Failed to add account"})

    def user_by_id(self, request: Request, response: Response):

        subject = User.find(request.param("user"))
        if subject is None:
            return response.json({"error": "No such user"})

        requestor_id = f"{self.user.gov_id}@afyamkononi"
        grantor_id = f"{subject.gov_id}@afyamkononi"

        consent_confirm = (
            Consent.where("requestor_id", requestor_id)
            .where("grantor_id", grantor_id)
            .first()
        )

        if consent_confirm is None and requestor_id != grantor_id:
            consent = Consent()
            consent.requestor_id = requestor_id
            consent.requestor_name = self.user.name
            consent.grantor_id = grantor_id
            consent.grantor_name = subject.name
            consent.permission = "can_set_my_account_detail"
            consent.save()
            return response.json(
                {
                    "error": "No such permissions. This owner has been requested to grant permissions."
                }
            )
        elif (
            consent_confirm is not None
            and consent_confirm.grantor_id != requestor_id
            and consent_confirm.status != "granted"
        ):
            consent_confirm.update(status="pending")
            return response.json(
                {
                    "error": "No such permissions. This owner has been requested to grant permissions."
                }
            )

        data = self.ibc.get_account_details(subject.gov_id)

        if data.detail == "":
            return response.json(
                {
                    "error": "No such permissions. This owner has been requested to grant permissions."
                }
            )

        return utils.format_query_result(data)

    def user_by_gov_id(self, request: Request, response: Response):

        subject = User.where("gov_id", request.param("user")).first()
        if subject is None:
            return response.json({"error": "No such user"})

        requestor_id = f"{self.user.gov_id}@afyamkononi"
        grantor_id = f"{subject.gov_id}@afyamkononi"

        consent_confirm = (
            Consent.where("requestor_id", requestor_id)
            .where("grantor_id", grantor_id)
            .first()
        )

        if consent_confirm is None and requestor_id != grantor_id:
            consent = Consent()
            consent.requestor_id = requestor_id
            consent.requestor_name = self.user.name
            consent.grantor_id = grantor_id
            consent.grantor_name = subject.name
            consent.permission = "can_set_my_account_detail"
            consent.save()
            return response.json(
                {
                    "error": "No such permissions. This owner has been requested to grant permissions."
                }
            )
        elif (
            consent_confirm is not None
            and consent_confirm.grantor_id != requestor_id
            and consent_confirm.status != "granted"
        ):
            consent_confirm.update(status="pending")
            return response.json(
                {
                    "error": "No such permissions. This owner has been requested to grant permissions."
                }
            )

        data = self.ibc.get_account_details(subject.gov_id)

        if data.detail == "":
            return response.json(
                {
                    "error": "No such permissions. This owner has been requested to grant permissions."
                }
            )

        return utils.format_query_result(data)

    def grant_edit_permissions(self, request: Request, response: Response):
        subject = User.where("gov_id", request.input("gov_id")).first()
        grantor = User.where("gov_id", request.param("user")).first()

        if subject is None:
            return response.json({"error": "No such user"})
        blockchain_status = self.ibc.grant_edit_permissions(subject)
        iroha_message = iroha_messages.grant_set_account_detail_perms_failed(
            blockchain_status
        )
        if iroha_message is not None:
            return response.json(iroha_message)

        (
            Consent.where("requestor_id", f"{subject.gov_id}@afyamkononi")
            .where("grantor_id", f"{grantor.gov_id}@afyamkononi")
            .update(status="granted")
        )

        return response.json({"success": "The requested permissions were granted"})

    def revoke_edit_permissions(self, request: Request, response: Response):
        subject = User.where("gov_id", request.input("gov_id")).first()
        grantor = User.where("gov_id", request.param("user")).first()

        if subject is None:
            return response.json({"error": "No such user"})
        blockchain_status = self.ibc.revoke_edit_permissions(subject)
        iroha_message = iroha_messages.revoke_set_account_detail_perms_failed(
            blockchain_status
        )
        if iroha_message is not None:
            return response.json(iroha_message)

        (
            Consent.where("requestor_id", f"{subject.gov_id}@afyamkononi")
            .where("grantor_id", f"{grantor.gov_id}@afyamkononi")
            .update(status="revoked")
        )

        return response.json({"success": "The requested permissions were revoked"})
