"""Welcome The User To Masonite."""

from masonite.view import View
from masonite.request import Request
from masonite.controllers import Controller

import app.http.modules.IrohaBlockchain as ib


class WelcomeController(Controller):
    """Controller For Welcoming The User."""

    def __init__(self, request: Request):
        """WelcomeController Initializer

        Arguments:
            request {masonite.request.Request} -- The Masonite Request class.
        """
        self.request = request

    def show(self, view: View, request: Request):
        """Show the welcome page.

        Arguments:
            view {masonite.view.View} -- The Masonite view class.
            request {masonite.request.Request} -- The Masonite request class.

        Returns:
            masonite.view.View -- The Masonite view class.
        """

        # ib.run()

        return view.render('welcome')
