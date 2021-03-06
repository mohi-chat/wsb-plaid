# Read env vars from .env file
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.investments_transactions_get_request_options import InvestmentsTransactionsGetRequestOptions
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.api import plaid_api
import plaid

from datetime import datetime
from datetime import timedelta
import base64
import os
import datetime
import requests
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import json
import time
from dotenv import load_dotenv
from pymongo import MongoClient

from fastapi import FastAPI, Form, Request
from pydantic import BaseModel
import uvicorn

from logger import Logger
from logger.custom_log_methods import logAPIError, logFunctionError
load_dotenv()

app = FastAPI()
app.add_middleware(Logger.RouteLoggerMiddleware)

# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')

# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
MONGO_DB = MongoClient(MONGODB_CONNECTION_STRING).explore

# Institution IDS (As per Plaid documentation)
# ============================================
ROBINHOOD = 'ins_54'
FIDELITY = 'ins_12'
# ============================================

def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'development':
    host = plaid.Environment.Development

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

# Parameters used for the OAuth redirect Link flow.
#
# Set PLAID_REDIRECT_URI to 'http://localhost:3000/'
# The OAuth redirect flow requires an endpoint on the developer's website
# that the bank website should redirect to. You will need to configure
# this redirect URI for your client ID through the Plaid developer dashboard
# at https://dashboard.plaid.com/team/api.
PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))


# We store the access_token in memory - in production, store it in a secure
# persistent data store.
access_token = None
item_id = None


@app.post('/api/info')
def info():
    global access_token
    global item_id
    return {
        'item_id': item_id,
        'access_token': access_token,
        'products': PLAID_PRODUCTS
    }


@app.post('/api/create_link_token')
def create_link_token():
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="Plaid Quickstart",
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language='en',
            webhook='https://us-central1-capital-group-infra.cloudfunctions.net/robinhood_refresh_webook',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            )
        )

        response = client.link_token_create(request)
        return response.to_dict()
    except plaid.ApiException as e:
        logFunctionError({
            "error_msg": " Error in create link token " ,
            "exception_msg": str(e),
            "function": "create_link_token",
            "parent_route": "/api/create_link_token"
        })
        return json.loads(e.body)

@app.post('/api/set_access_token')
def get_access_token(public_token: str = Form(...), email: str = Form(...)):
    global access_token
    global item_id
    try:
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        # Initiate background account link task.
        data = {
            "item_id": item_id,
            "access_token": access_token,
            "email": email,
            "environment": PLAID_ENV,
            "webhook_type": 'NEW_ACCOUNT_LINK'
        }
        url = "https://us-central1-capital-group-infra.cloudfunctions.net/robinhood_refresh_webook"
        response = requests.post(url, headers={"Content-Type":"application/json"}, data=json.dumps(data))

        return exchange_response.to_dict()
    except plaid.ApiException as e:
        logFunctionError({
            "error_msg": " Error in getting the access token" ,
            "exception_msg": json.dumps(e.body),
            "function": "get_access_token",
            "parent_route": "/api/set_access_token"
        })
        return json.loads(e.body)


@app.get('/api/auth')
def get_auth():
    try:
       request = AuthGetRequest(
            access_token=access_token
        )
       response = client.auth_get(request)
       pretty_print_response(response.to_dict())
       return response.to_dict()
    except plaid.ApiException as e:
        error_response = format_error(e)
        logFunctionError({
            "error_msg": " Error in getting auth" ,
            "exception_msg": json.dumps(error_response),
            "function": "get_auth",
            "parent_route": "/api/auth"
        })
        return error_response

# Retrieve high-level information about an Item
# https://plaid.com/docs/#retrieve-item


def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True, default=str))

def format_error(e):
    response = json.loads(e.body)
    return {'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}

if __name__ == '__main__':
    uvicorn.run('server:app', host='0.0.0.0', port=8000)
