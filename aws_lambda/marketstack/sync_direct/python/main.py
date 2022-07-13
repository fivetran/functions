import json
import boto3
from botocore.vendored import requests

def lambda_handler(request, context):

    # Fetch records using api calls
    (insert, delete, state, hasMore) = api_response(request['state'], request['secrets'])

    # Mention schema
    tickersSchema = {}
    tickersSchema['primary_key'] = ['symbol']
    tickersPriceSchema={}
    tickersPriceSchema['primary_key'] = ['symbol']

    schema = {}
    schema['tickers']=tickersSchema
    schema['tickers_price']=tickersPriceSchema

    # Populate response
    response = {}
    # Add updated state to response
    response['state'] =  state
    # Add schema defintion in response
    response['schema'] = schema
    # Add hasMore flag
    response['hasMore'] = hasMore
    # Add all the records to be inserted in response
    response['insert'] = insert
    # Add all the records to be marked as deleted in response
    response['delete'] = delete

    return response

def api_response(state, secrets):

    # Initialize state
    if(state):
        ticker_offset = state["ticker_offset"]
    else:
        ticker_offset = 0

    insert_tickers = get_tickers(secrets['apiKey'],ticker_offset)

    # Increment offset
    ticker_offset+=5

    state,insert,delete,hasMore = {},{},{},False

    # Fetch only 10 tickers
    if(not insert_tickers):
        ticker_offset=0
    else:
        if(ticker_offset>=10):
            ticker_offset=0
        else:
            hasMore=True

    insert_ticker_price=[]
    for ticker in insert_tickers:
        temp_list=get_ticker_price(secrets['apiKey'],ticker['symbol'])
        if(temp_list[0]):
            insert_ticker_price.append(temp_list[0])

    insert['tickers'] = insert_tickers
    delete['tickers']=[]
    state['ticker_offset']=ticker_offset

    insert['tickers_price'] = insert_ticker_price
    delete['tickers_price'] = []

    return (insert, delete, state, hasMore)

def get_tickers(api_key,ticker_offset):
    params = {
    'access_key': api_key,
    'offset': ticker_offset,
    'limit': 5
    }
    api_result = requests.get('http://api.marketstack.com/v1/tickers', params)
    api_response = api_result.json()
    insert_records=api_response["data"]
    return insert_records

def get_ticker_price(api_key,symbols):
    params = {
    'access_key': api_key,
    'symbols':symbols
    }
    api_result = requests.get('http://api.marketstack.com/v1/eod/latest', params)
    api_response = api_result.json()
    insert_records=api_response["data"]
    return insert_records
