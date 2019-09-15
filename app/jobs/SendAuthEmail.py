"""A SendAuthEmail Queue Job."""

from app.User import User

from masonite.queues import Queueable
from masonite import Mail

class SendAuthEmail(Queueable):
    """A SendAuthEmail Job."""

    def __init__(self, user_details: User):
        """A SendAuthEmail Constructor."""
        self.user_details = user_details
        

    def handle(self, mail: Mail):
        """
        Logic to send email.
        """
        print("Ru9000gfsdfg484888un")
        mail.to(self.user_details.email).template(
            "mail/auth_email", {"user": self.user_details}
        ).send()
    
    def failed(self, payload, error):
        print(f'Payload: {payload}')
        print(f'Error: {error}')
