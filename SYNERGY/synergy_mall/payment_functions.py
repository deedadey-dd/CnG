import os
import requests
import json


# Define your Paystack secret key
PAYSTACK_SECRET_KEY = os.getenv('PAY_SECRET')

# Paystack API endpoint for initializing a transaction
PAYSTACK_INIT_TRANSACTION_URL = 'https://api.paystack.co/transaction/initialize'


def initialize_payment(email, amount):
    """
    Initialize a Paystack payment
    :param email: Customer's email address
    :param amount: Transaction amount in kobo (for NGN, multiply Naira by 100)
    """
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    # Paystack requires the amount to be in the lowest currency unit (e.g., kobo for NGN)
    payload = {
        "email": email,
        "amount": amount  # Amount in kobo, so for 1000 NGN, pass 100000
    }

    try:
        # Send the request to Paystack
        response = requests.post(PAYSTACK_INIT_TRANSACTION_URL, headers=headers, data=json.dumps(payload))

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            if response_data['status']:
                # Extract the authorization URL where the user will make the payment
                authorization_url = response_data['data']['authorization_url']
                return authorization_url
            else:
                return f"Error: {response_data['message']}"
        else:
            return f"Failed to initialize payment. Status Code: {response.status_code}"
    except requests.RequestException as e:
        return f"An error occurred: {str(e)}"

