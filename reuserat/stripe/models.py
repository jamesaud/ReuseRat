from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator


# Docs for EmailAddress at: #https://github.com/pennersr/django-allauth/blob/master/allauth/account/models.py
from allauth.account.models import EmailAddress

# These should be hidden from the users as we are managing their stripe accounts(Managed).

FOUR_DIGIT_VALIDATOR = RegexValidator(regex='^\d{4}$', message='Has to be 4 integers', code='nomatch')


class TransactionPaymentTypeChoices:
    """
    Used for the 'PaymentType' in Transaction. 
    'Payment Type' shouldn't have the 'choices=CHOICES' because some of the choices come from the user model PaymentTypeChoices, which we cannot import due to 
    circular dependencies. Data integrity is much more important in the user model, so the choices for Transaction 'Payment Type' are not enforced.
    However, we still want the choices to be consistent so import these constants when creating a Transaction object.
    """
    ITEM_SOLD = 'Item Sold'  # Used for the 'payment_type' in the the transaction model.


class TransactionTypeChoices:
    IN = 'Funds Added'        #  Money added to user's Stripe account                          
    OUT = 'Cash Out'          #  Money being cashed out from a user's Stripe account                           
    CREDIT = 'Credit'         # Store Credit added to account 
    FEE = 'Fee'               # Charging the user's Stripe account for something                                 
    Choices = (
        (IN, 'Funds Added'),   
        (OUT, 'Cash Out'),
        (CREDIT, 'Credit'),
        (FEE, 'Fee')
    )

class StripeAccount(models.Model):

    account_id = models.CharField(_('stripe AccountId'), blank=False, max_length=255, primary_key=True) # Stripe account ID
    secret_key = models.CharField(_('stripe Secret'), blank=False, max_length=255)
    publishable_key = models.CharField(_('stripe Publishable'), blank=False, max_length=255)

    # This is the bank account information.
    account_holder_name = models.CharField(max_length=255, null=True, blank=False)
    account_number_last_four = models.CharField(validators=[FOUR_DIGIT_VALIDATOR], max_length=4, null=True, blank=False)
    account_number_length = models.IntegerField(null=True, blank=False)
    routing_number_last_four = models.CharField(validators=[FOUR_DIGIT_VALIDATOR], max_length=4, null=True, blank=False)
    # Length of routing number is 9 digits per USA banking regulations.

    def has_bank(self):
        return True if (self.routing_number_last_four and self.account_number_last_four) else False

    def retrieve_balance(self):
        """Returns the Stripe balance in cents"""
        from .helpers import retrieve_balance # Avoid circular import collision.
        return retrieve_balance(self.secret_key)


class PaypalAccount(models.Model):
    email = models.OneToOneField(EmailAddress)


class Transaction(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    payment_type = models.CharField(_('Payment Type'), max_length=255)
    amount = models.FloatField() # In dollars
    type = models.CharField(_("Transaction Type"), choices=TransactionTypeChoices.Choices, max_length=255)
    message = models.CharField(max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{type} with {payment} for {user}'.format(user=self.user, payment=self.payment_type, type=self.type)
    
