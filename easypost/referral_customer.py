from typing import (
    Any,
    Dict,
    List,
    Optional,
)

import requests

from easypost.constant import TIMEOUT
from easypost.easypost_object import convert_to_easypost_object
from easypost.error import Error
from easypost.requestor import (
    RequestMethod,
    Requestor,
)


class ReferralCustomer:
    @staticmethod
    def create(
        api_key: Optional[str] = None,
        **params,
    ) -> Dict[str, Any]:
        """Create a referral customer.

        This function requires the Partner User's API key.
        """
        requestor = Requestor(local_api_key=api_key)
        new_params = {"user": params}
        response, api_key = requestor.request(
            method=RequestMethod.POST,
            url="/referral_customers",
            params=new_params,
        )
        return convert_to_easypost_object(response=response, api_key=api_key)

    @staticmethod
    def update_email(
        email,
        user_id,
        api_key: Optional[str] = None,
    ) -> bool:
        """Update a referral customer.

        This function requires the Partner User's API key.
        """
        requestor = Requestor(local_api_key=api_key)
        url = f"/referral_customers/{user_id}"
        wrapped_params = {
            "user": {
                "email": email,
            }
        }
        _, _ = requestor.request(
            method=RequestMethod.PUT,
            url=url,
            params=wrapped_params,
        )

        # Return true if succeeds, an error will be thrown if it fails
        return True

    @staticmethod
    def all(
        api_key: Optional[str] = None,
        **params,
    ) -> List:
        """Retrieve a list of referral customers.

        This function requires the Partner User's API key.
        """
        requestor = Requestor(local_api_key=api_key)
        response, api_key = requestor.request(
            method=RequestMethod.GET,
            url="/referral_customers",
            params=params,
        )
        return convert_to_easypost_object(response=response, api_key=api_key)

    @classmethod
    def get_next_page(
        cls,
        referrals: Dict[str, Any],
        page_size: int,
        api_key: Optional[str] = None,
    ) -> List["ReferralCustomer"]:
        """Retrieve next page of a referral customers."""
        requestor = Requestor(local_api_key=api_key)
        url = "/referral_customers"
        referral_array = referrals["referral_customers"]

        if referral_array is None or len(referral_array) == 0 or not referrals.get("has_more"):
            raise Error(message="There are no more pages to retrieve.")

        params = {
            "before_id": referral_array[-1].id,
            "page_size": page_size,
        }

        response, api_key = requestor.request(method=RequestMethod.GET, url=url, params=params)
        if response is None or len(response["referral_customers"]) == 0 or not response["has_more"]:
            raise Error(message="There are no more pages to retrieve.")

        return convert_to_easypost_object(response=response, api_key=api_key)

    @staticmethod
    def add_credit_card(
        referral_api_key: str,
        number: str,
        expiration_month: int,
        expiration_year: int,
        cvc: str,
        priority: str = "primary",
    ) -> Dict[str, Any]:
        """Add credit card to a referral customer.

        This function requires the ReferralCustomer User's API key.
        """
        easypost_stripe_api_key = ReferralCustomer._retrieve_easypost_stripe_api_key()

        try:
            stripe_token = ReferralCustomer._create_stripe_token(
                number,
                expiration_month,
                expiration_year,
                cvc,
                easypost_stripe_api_key,
            )
        except Exception:
            raise Error(message="Could not send card details to Stripe, please try again later")

        response = ReferralCustomer._create_easypost_credit_card(
            referral_api_key,
            stripe_token.get("id", ""),
            priority=priority,
        )
        return convert_to_easypost_object(response)

    @staticmethod
    def _retrieve_easypost_stripe_api_key() -> str:
        """Retrieve EasyPost's Stripe public API key."""
        requestor = Requestor()
        public_key, _ = requestor.request(
            method=RequestMethod.GET,
            url="/partners/stripe_public_key",
        )
        return public_key.get("public_key", "")

    @staticmethod
    def _create_stripe_token(
        number: str,
        expiration_month: int,
        expiration_year: int,
        cvc: str,
        easypost_stripe_key: str,
    ) -> Dict[str, Any]:
        """Get credit card token from Stripe."""
        headers = {
            # This Stripe endpoint only accepts URL form encoded bodies
            "Content-type": "application/x-www-form-urlencoded",
        }

        credit_card_dict = {
            "card": {
                "number": number,
                "exp_month": expiration_month,
                "exp_year": expiration_year,
                "cvc": cvc,
            }
        }

        form_encoded_params = Requestor.form_encode_params(credit_card_dict)
        url = "https://api.stripe.com/v1/tokens"

        stripe_response = requests.post(
            url,
            params=form_encoded_params,
            headers=headers,
            auth=requests.auth.HTTPBasicAuth(easypost_stripe_key, ""),
            timeout=TIMEOUT,
        )
        return stripe_response.json()

    @staticmethod
    def _create_easypost_credit_card(
        referral_api_key: str,
        stripe_object_id: str,
        priority: str = "primary",
    ) -> Dict[str, Any]:
        """Submit Stripe credit card token to EasyPost."""
        requestor = Requestor(local_api_key=referral_api_key)

        params = {
            "credit_card": {
                "stripe_object_id": stripe_object_id,
                "priority": priority,
            }
        }

        response, _ = requestor.request(
            method=RequestMethod.POST,
            params=params,
            url="/credit_cards",
        )
        return response