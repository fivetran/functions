import json
import boto3
from botocore.vendored import requests
from datetime import date
import time

def lambda_handler(request, context):

    state=request['state']
    # Initialize state
    if(not state):
        state["ticker_offset"] = 0
        state["ticker_start_cursor"]="2000-01-01"
        state["ticker_end_cursor"]=str(date.today())

    # Fetch data to the latest date if ticker_offset is 0
    if(state["ticker_offset"]==0):
        state["ticker_end_cursor"]=str(date.today())

    # Fetch records using api calls
    (insert, delete, state, hasMore) = api_response(state, request['secrets'])

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

    #Populate inserts and deletes.
    response_s3={}
    # Add all the records to be inserted in response
    response_s3['insert'] = insert
    # Add all the records to be marked as deleted in response
    response_s3['delete'] = delete

    # Store the data(inserts and deletes) in s3 file
    json_str = bytes(json.dumps(response_s3).encode("utf-8"))
    push_data_s3(request, json_str)

    return response

def api_response(state, secrets):

    ticker_offset = state["ticker_offset"]
    ticker_start_cursor=state["ticker_start_cursor"]
    ticker_end_cursor=state["ticker_end_cursor"]

    # Fetch all the tickers
    insert_tickers = get_tickers(secrets['apiKey'],ticker_offset)

    state,insert,delete,hasMore = {},{},{},False

    # Stop when no more ticker is left
    if(not insert_tickers):
        ticker_offset=0
        ticker_start_cursor=ticker_end_cursor
        ticker_end_cursor=str(date.today())
    else:
        hasMore=True

    insert_ticker_price=[]
    insert_ticker_actual=[]

    # Fetch the records of prices. If time exceeds 5s then return intermediate response and fetch other records in subsequent calls
    start_time=time.time()
    for ticker in insert_tickers:
        temp_list=get_ticker_price(secrets['apiKey'],ticker['symbol'],ticker_start_cursor,ticker_end_cursor)
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
    state['ticker_start_cursor']=ticker_start_cursor
    state['ticker_end_cursor']=ticker_end_cursor

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
    insert_ticker_records=api_response["data"]
    return insert_ticker_records


# This function will fetch the prices of a particular ticker from start date to end date
# Params-1] access_key: The api token for accessing data
#        2] symbol: ticker for which price is to be calculated
#        3] limit: Maximum number of records in one call
#        4] offset: cursor value
#        5] date_from: starting date to fetch records
#        6] date_to: end date to fetch records
def get_ticker_price(api_key,symbols,ticker_start_cursor,ticker_end_cursor):
    ticker_price_offset=0
    insert_ticker_price_records=[]
    while(True):
        params = {
        'access_key': api_key,
        'symbols':symbols,
        'limit': 1000,
        'offset': ticker_price_offset,
        'date_from':ticker_start_cursor,
        'date_to':ticker_end_cursor
        }
        api_result = requests.get('http://api.marketstack.com/v1/eod', params)
        api_response = api_result.json()
        insert_ticker_price_records_temp=api_response["data"]
        if(insert_ticker_price_records_temp):
            insert_ticker_price_records+=insert_ticker_price_records_temp
            ticker_price_offset+=1000
        else:
            break
    return insert_ticker_price_records

# Function to store data in S3 bucket
def push_data_s3(request, json_str):
    client = boto3.client('s3')
    client.put_object(Body=json_str, Bucket=request["bucket"], Key=request["file"])
