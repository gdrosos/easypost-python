import os
from unittest.mock import patch

import pytest

import easypost
from easypost.error import Error


REFERRAL_CUSTOMER_PROD_API_KEY = os.getenv("REFERRAL_CUSTOMER_PROD_API_KEY", "123")


@pytest.mark.vcr()
def test_referral_customer_create(partner_prod_api_key):
    """This test requires a partner customer's production API key via PARTNER_USER_PROD_API_KEY."""
    created_referral_customer = easypost.ReferralCustomer.create(
        name="test test",
        email="test@test.com",
        phone="8888888888",
    )

    assert isinstance(created_referral_customer, easypost.User)
    assert str.startswith(created_referral_customer.id, "user_")
    assert created_referral_customer.name == "test test"


@pytest.mark.vcr()
def test_referral_customer_update(partner_prod_api_key):
    """This test requires a partner customer's production API key via PARTNER_USER_PROD_API_KEY."""
    referral_customers = easypost.ReferralCustomer.all()

    try:
        easypost.ReferralCustomer.update_email(
            "email@example.com",
            referral_customers.referral_customers[0].id,
        )
    except Exception:
        assert False


@pytest.mark.vcr()
def test_referral_customer_all(partner_prod_api_key, page_size):
    """This test requires a partner customer's production API key via PARTNER_USER_PROD_API_KEY."""
    referral_customers = easypost.ReferralCustomer.all(page_size=page_size)

    referral_customers_array = referral_customers["referral_customers"]

    assert len(referral_customers_array) <= page_size
    assert referral_customers["has_more"] is not None
    assert all(isinstance(referral_customer, easypost.User) for referral_customer in referral_customers_array)


@pytest.mark.vcr()
def test_referral_get_next_page(partner_prod_api_key, page_size):
    try:
        referrals = easypost.ReferralCustomer.all(page_size=page_size)
        next_page = easypost.ReferralCustomer.get_next_page(referrals=referrals, page_size=page_size)

        first_id_of_first_page = referrals["referral_customers"][0].id
        first_id_of_second_page = next_page["referral_customers"][0].id

        assert first_id_of_first_page != first_id_of_second_page
    except Error as e:
        if e.message != "There are no more pages to retrieve.":
            raise Error(message="Test failed intentionally.")


# PyVCR is having troubles matching the body of the form-encoded data here, override the default
@pytest.mark.vcr(
    match_on=[
        "headers",
        "method",
        "query",
        "uri",
    ]
)
def test_referral_customer_add_credit_card(partner_prod_api_key, credit_card_details):
    """This test requires a partner customer's production API key via PARTNER_USER_PROD_API_KEY
    as well as one of that customer's referral's production API keys via REFERRAL_CUSTOMER_PROD_API_KEY.
    """
    added_credit_card = easypost.ReferralCustomer.add_credit_card(
        referral_api_key=REFERRAL_CUSTOMER_PROD_API_KEY,
        number=credit_card_details["number"],
        expiration_month=credit_card_details["expiration_month"],
        expiration_year=credit_card_details["expiration_year"],
        cvc=credit_card_details["cvc"],
    )

    assert str.startswith(added_credit_card.id, "card_")
    assert added_credit_card.last4 == "6170"


@patch("easypost.referral_customer.ReferralCustomer._retrieve_easypost_stripe_api_key")
@patch("easypost.referral_customer.ReferralCustomer._create_stripe_token", side_effect=Exception())
def test_referral_add_credit_card_error(mock_stripe_token, mock_easypost_key, credit_card_details):
    """This test requires a partner customer's production API key via PARTNER_USER_PROD_API_KEY
    as well as one of that customer's referral's production API keys via REFERRAL_CUSTOMER_PROD_API_KEY.
    """
    with pytest.raises(Exception) as error:
        _ = easypost.ReferralCustomer.add_credit_card(
            referral_api_key=REFERRAL_CUSTOMER_PROD_API_KEY,
            number=credit_card_details["number"],
            expiration_month=credit_card_details["expiration_month"],
            expiration_year=credit_card_details["expiration_year"],
            cvc=credit_card_details["cvc"],
        )

    assert str(error.value) == "Could not send card details to Stripe, please try again later"
