"""User Model."""

from config.database import Model


class User(Model):
    """
        User Model Definition (generated with love by Masonite) 
        
        id: integer default: None
        gov_id: string(255) default: None
        name: string(255) default: None
        email: string(255) default: None
        phone_number: string(255) default: None
        password: string(255) default: None
        private_key: string(255) default: None
        public_key: string(255) default: None
        type: string(255) default: None
        remember_token: string(255) default: None
        verified_at: datetime default: None
        created_at: datetime default: CURRENT_TIMESTAMP(6)
        updated_at: datetime default: CURRENT_TIMESTAMP(6)
    """

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

    __hidden__ = [
        "password",
        "public_key",
        "private_key",
        "remember_token",
        "verified_at",
    ]
