"""Consent Model."""

from config.database import Model


class Consent(Model):
    """Consent Model Definition (generated with love by Masonite) 
        id: integer default: None
        requestor_id: string(50) default: None
        grantor_id: string(50) default: None
        requestor_name: string(100) default: None
        grantor_name: string(100) default: None
        permission: string(255) default: None
        status: string(255) default: pending
        created_at: datetime default: CURRENT_TIMESTAMP(6)
        updated_at: datetime default: CURRENT_TIMESTAMP(6)
    """

    __fillable__ = [
        "requestor_id",
        "grantor_id",
        "requestor_name",
        "grantor_name",
        "permission",
        "status",
    ]
