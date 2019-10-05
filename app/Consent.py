"""Consent Model."""

from config.database import Model


class Consent(Model):
    """Consent Model."""

    __fillable__ = ["requestor", "grantor", "permission", "status"]
