from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from easypost.easypost_object import convert_to_easypost_object
from easypost.error import Error
from easypost.requestor import (
    RequestMethod,
    Requestor,
)
from easypost.resource import Resource


class Billing(Resource):
    @classmethod
    def fund_wallet(cls, amount: str, priority: str = "primary", api_key: Optional[str] = None) -> None:
        """Fund your EasyPost wallet by charging your primary or secondary payment method on file."""
        endpoint, payment_method_id = Billing._get_payment_method_info(priority=priority)

        requestor = Requestor(local_api_key=api_key)
        url = f"{endpoint}/{payment_method_id}/charges"
        wrapped_params = {"amount": amount}
        requestor.request(method=RequestMethod.POST, url=url, params=wrapped_params)

    @classmethod
    def delete_payment_method(cls, priority: str, api_key: Optional[str] = None) -> None:
        """Delete a payment method."""
        endpoint, payment_method_id = Billing._get_payment_method_info(priority=priority)

        requestor = Requestor(local_api_key=api_key)
        url = f"{endpoint}/{payment_method_id}"
        requestor.request(method=RequestMethod.DELETE, url=url)

    @classmethod
    def retrieve_payment_methods(cls, api_key: Optional[str] = None, **params) -> Dict[str, Any]:
        """Retrieve payment methods."""
        requestor = Requestor(local_api_key=api_key)
        response, api_key = requestor.request(method=RequestMethod.GET, url="/payment_methods", params=params)

        if response.get("id") is None:
            raise Error(message="Billing has not been setup for this user. Please add a payment method.")

        return convert_to_easypost_object(response=response, api_key=api_key)

    @classmethod
    def _get_payment_method_info(cls, priority: str = "primary") -> List[str]:
        """Get payment method info (type of the payment method and ID of the payment method)"""
        payment_methods = Billing.retrieve_payment_methods()

        payment_method_map = {
            "primary": "primary_payment_method",
            "secondary": "secondary_payment_method",
        }

        payment_method_to_use = payment_method_map.get(priority)
        error_string = "The chosen payment method is not valid. Please try again."

        if payment_method_to_use and payment_methods[payment_method_to_use]:
            payment_method_id = payment_methods[payment_method_to_use]["id"]
            if payment_method_id.startswith("card_"):
                endpoint = "/credit_cards"
            elif payment_method_id.startswith("bank_"):
                endpoint = "/bank_accounts"
            else:
                raise Error(message=error_string)
        else:
            raise Error(message=error_string)

        return [endpoint, payment_method_id]
