"""User Model."""

from config.database import Model


class User(Model):
    """User Model."""

    __fillable__ = [
        "gov_id",
        "name",
        "email",
        "phone_number",
        "password",
        "public_key",
        "private_key",
        "type",
    ]

    __auth__ = "email"

    __hidden__ = ["password", "public_key", "private_key"]
