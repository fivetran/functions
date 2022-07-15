import json
from botocore.vendored import requests
from datetime import date
import time

def lambda_handler(request, context):

    # Fetch records using api calls
    (insert, delete, state, hasMore) = api_response(request['state'], request['secrets'])

    # Mention schema
    tickersSchema = {}
    tickersSchema['primary_key'] = ['symbol']
    tickersPriceSchema={}
    tickersPriceSchema['primary_key'] = ['symbol','date']

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
        start_date=state["state_date"]
    else:
        ticker_offset = 0
        start_date="2000-01-01"

    # Fetch data to the latest date
    end_date=str(date.today())

    # Fetch all the tickers
    insert_tickers = get_tickers(secrets['apiKey'],ticker_offset)

    state,insert,delete,hasMore = {},{},{},False

    # Stop when no more ticker is left
    if(not insert_tickers):
        ticker_offset=0
        start_date=end_date
    else:
        hasMore=True

    insert_ticker_price=[]
    insert_ticker_actual=[]

    # Fetch the records of prices. If time exceeds 5s then return intermediate response and fetch other records in subsequent calls
    start_time=time.time()
    for ticker in insert_tickers:
        temp_list=get_ticker_price(secrets['apiKey'],ticker['symbol'],start_date,end_date)
        ticker_offset+=1
        if(temp_list):
            insert_ticker_price+=temp_list
            insert_ticker_actual.append(ticker)
        end_time=time.time()
        if(end_time-start_time>5):
            break


    insert['tickers'] = insert_ticker_actual
    delete['tickers']=[]
    state['ticker_offset']=ticker_offset
    state['state_date']=start_date

    insert['tickers_price'] = insert_ticker_price
    delete['tickers_price'] = []

    return (insert, delete, state, hasMore)


# This function will list all the tickers presently available
# Params-1] access_key: The api token for accessing data
#        2] offset : cursor value
#        3] limit : Maximum number of records in one call
def get_tickers(api_key,ticker_offset):
    params = {
    'access_key': api_key,
    'offset': ticker_offset,
    'limit': 1000
    }
    api_result = requests.get('http://api.marketstack.com/v1/tickers', params)
    api_response = api_result.json()
    insert_records=api_response["data"]
    return insert_records


# This function will fetch the prices of a particular ticker from start date to end date
# Params-1] access_key: The api token for accessing data
#        2] symbol: ticker for which price is to be calculated
#        3] limit: Maximum number of records in one call
#        4] offset: cursor value
#        5] date_from: starting date to fetch records
#        6] date_to: end date to fetch records
def get_ticker_price(api_key,symbols,start_date,end_date):
    ticker_price_offset=0
    insert_records=[]
    while(True):
        params = {
        'access_key': api_key,
        'symbols':symbols,
        'limit': 1000,
        'offset': ticker_price_offset,
        'date_from':start_date,
        'date_to':end_date
        }
        api_result = requests.get('http://api.marketstack.com/v1/eod', params)
        api_response = api_result.json()
        insert_records_temp=api_response["data"]
        if(insert_records_temp):
            insert_records+=insert_records_temp
            ticker_price_offset+=1000
        else:
            break
    return insert_records
