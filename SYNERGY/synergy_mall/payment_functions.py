import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Define your Paystack secret key
PAYSTACK_SECRET_KEY = 'YOUR_SECRET_KEY'

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


@csrf_exempt
def paystack_webhook(request):
    if request.method == 'POST':
        # Get the request body and decode it
        event = json.loads(request.body.decode('utf-8'))

        # Retrieve the event type and details
        event_type = event.get('event', None)
        data = event.get('data', {})

        # Paystack sends different events, we are only interested in 'charge.success'
        if event_type == 'charge.success':
            # Verify the event by contacting Paystack's API
            payment_reference = data.get('reference')

            if payment_reference:
                verified = verify_paystack_payment(payment_reference)

                if verified:
                    # Mark payment as successful in your database (implement this)
                    return JsonResponse({'status': 'success', 'message': 'Payment verified'}, status=200)
                else:
                    return JsonResponse({'status': 'error', 'message': 'Payment verification failed'}, status=400)

        # Return a generic response for unsupported event types
        return JsonResponse({'status': 'success'}, status=200)

    return JsonResponse({'status': 'invalid request'}, status=400)


def verify_paystack_payment(reference):
    """
    Verify the payment reference with Paystack API to confirm payment.
    """
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('status') and response_data['data']['status'] == 'success'

    return False
