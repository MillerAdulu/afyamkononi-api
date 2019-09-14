"""User Model."""

from config.database import Model


class User(Model):
    """User Model."""

    __fillable__ = ['name', 'email', 'password', 'public_key', 'private_key',
                    'type']

    __auth__ = 'email'

    __hidden__ = ['password', 'public_key', 'private_key']
