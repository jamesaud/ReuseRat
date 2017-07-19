from reuserat.users.models import User
from reuserat.stripe.models import StripeAccount
from reuserat.stripe.helpers import create_account, update_account
from django.conf import settings
from reuserat.stripe.models import StripeAccount, PaypalAccount
from django.contrib import messages

import logging
from config.logging import setup_logger


setup_logger()
# Get an instance of a logger
logger = logging.getLogger(__name__)



class FixMissingStripeAccountMiddleWare:


    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # So the sign up view will work

        if request.user.is_authenticated and request.user.has_completed_signup() and (not self.has_valid_stripe_account(request.user)):
            user = request.user

            # Prepare user to redo the user_complete_signup_view by deleteing their stripe and paypal objects.
            try:
                user.stripe_account.delete()
                user.stripe_account = None
                user.save()
            except AttributeError:
                # Account didn't exist in the first place.
                pass

            stripe_account_instance = create_account(request.META['REMOTE_ADDR'])
            user.stripe_account = stripe_account_instance
            user.save()

            update_account(user.stripe_account.account_id,
                                          first_name=user.first_name,
                                          last_name=user.last_name,
                                          address_line=user.address.get_full_address_line(),
                                          address_city=user.address.city,
                                          address_state=user.address.state,
                                          address_zip=user.address.zipcode,
                                          )

            logging.info("Fixing Stripe Account for User: {}".format(user))

        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response



    @staticmethod
    def has_valid_stripe_account(user: User):
        if not user.stripe_account or (user.stripe_account.account_id is None):
            return False

        if settings.PRODUCTION:
            if user.stripe_account.publishable_key.startswith("sk_test"):
                return False

            if user.stripe_account.secret_key.startswith("sk_test"):
                return False

        return True



