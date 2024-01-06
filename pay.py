import requests
from requests.auth import HTTPBasicAuth
from src.conf.config import settings

CLIENT = settings.paypal_client
SECRET = settings.paypal_secret


def get_payment():
    auth = HTTPBasicAuth(CLIENT, SECRET)
    headers = {'Content-Type': 'application/json'}
    payload = {
        'intent': 'sale',
        'payer': {'payment_method': 'paypal'},
        'transactions': [{
            'amount': {
                'total': '1.00',
                'currency': 'USD'
            }
        }],
        'redirect_urls': {
            'return_url': 'http://localhost:8000/payment/execute',
            'cancel_url': 'http://localhost:8000/payment/cancel'
        }
    }

    response = requests.post('https://api.sandbox.paypal.com/v1/payments/payment',
                             json=payload, auth=auth, headers=headers)
    if response.status_code == 201:
        pay = response.json().get('links')
        print(pay[1].get('href'))
    else:
        return response.status_code


if __name__ == '__main__':
    print(get_payment())
