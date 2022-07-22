import json
from botocore.vendored import requests
from datetime import date
import time
import traceback


def lambda_handler(request, context):
    """This function is called by aws lambda

    Args:
        request (json): api request sent by connector
        context (json): context

    Returns:
        json: if successfull then connector response else error response
    """
    try:
        # Initialize state
        state = initialize_state(request['state'])

        # Fetch records using api calls
        (insert, delete, state, hasMore) = api_response(
            state, request['secrets'])

        # Get Response
        response = get_response(insert, delete, state, hasMore)

        # Return Response
        return response

    except Exception as e:
        # Return error response
        return {"errorMessage": str(e),
                "stackTrace": traceback.format_exc()}


def api_response(state, secrets):

    ticker_offset = state["ticker_offset"]
    ticker_start_cursor = state["ticker_start_cursor"]
    ticker_end_cursor = state["ticker_end_cursor"]

    # Fetch all the tickers
    insert_tickers = get_tickers(secrets['apiKey'], ticker_offset)

    # Fetch the records of prices of tickers.
    # If time exceeds 1s then return intermediate response and fetch other records in subsequent calls
    # After price for a ticker is fetched we increment ticker offset by 1
    insert_ticker_price = []
    insert_ticker_actual = []
    start_time = time.time()
    for ticker in insert_tickers:
        temp_list = get_ticker_price(
            secrets['apiKey'], ticker['symbol'], ticker_start_cursor, ticker_end_cursor)
        ticker_offset += 1
        if(temp_list):
            insert_ticker_price += temp_list
            insert_ticker_actual.append(ticker)
        end_time = time.time()
        if(end_time-start_time > 1):
            break

    state, insert, delete, hasMore = {}, {}, {}, False

    # If insert_tickers is empty then all tickers are processed
    #   Set ticker_offset back to 0 for again syncing from start in next sync
    #   Set ticker_start_cursor to ticker_end_cursor
    #   Set ticker_end_cursor to Today's date
    # Else
    #   Set hasMore = True to again run lambda function with updated cursor value
    if(not insert_tickers):
        ticker_offset = 0
        ticker_start_cursor = ticker_end_cursor
        ticker_end_cursor = str(date.today())
    else:
        hasMore = True

    # Populate insert, delete and state
    insert['tickers'] = insert_ticker_actual
    delete['tickers'] = []

    insert['tickers_price'] = insert_ticker_price
    delete['tickers_price'] = []

    state['ticker_offset'] = ticker_offset
    state['ticker_start_cursor'] = ticker_start_cursor
    state['ticker_end_cursor'] = ticker_end_cursor

    return (insert, delete, state, hasMore)


def get_tickers(api_key, ticker_offset):
    """This is a function to list all the tickers presently available

    Args:
        api_key (String): The api token for accessing data
        ticker_offset (int): Ticker cursor value

    Raises:
        Exception: When request fails or tickers cannot be fetched from response

    Returns:
        list: tickers
    """
    params = {
        'access_key': api_key,
        'offset': ticker_offset,
        'limit': 1000
    }
    try:
        api_result = requests.get(
            'http://api.marketstack.com/v1/tickers', params)
        api_response = api_result.json()
        insert_ticker_records = api_response["data"]
    except:
        raise Exception("Failed Fetching tickers, Error: " +
                        json.dumps(api_response))
    return insert_ticker_records


def get_ticker_price(api_key, symbols, ticker_start_cursor, ticker_end_cursor):
    """This is a function to fetch the prices of a particular ticker from start date to end date

    Args:
        api_key (String): The api token for accessing data
        symbols (String): Ticker for which price is to be calculated
        ticker_start_cursor (String): Starting date to fetch records
        ticker_end_cursor (String): End date to fetch records

    Raises:
        Exception: When request fails or ticker prices cannot be fetched from response

    Returns:
        list: ticker prices for particular ticker
    """
    ticker_price_offset = 0
    insert_ticker_price_records = []
    while(True):
        params = {
            'access_key': api_key,
            'symbols': symbols,
            'limit': 1000,
            'offset': ticker_price_offset,
            'date_from': ticker_start_cursor,
            'date_to': ticker_end_cursor
        }
        try:
            api_result = requests.get(
                'http://api.marketstack.com/v1/eod', params)
            api_response = api_result.json()
            insert_ticker_price_records_temp = api_response["data"]
            if(insert_ticker_price_records_temp):
                insert_ticker_price_records += insert_ticker_price_records_temp
                ticker_price_offset += 1000
            else:
                break
        except:
            raise Exception(
                "Failed Fetching ticker prices, Error: " + json.dumps(api_response))
    return insert_ticker_price_records


def get_response(insert, delete, state, hasMore):
    """This is a function to return Response to be sent to connector

    Args:
        insert (json): insert records
        delete (json): delete records
        state (json): state of connector
        hasMore (bool): hasMore value in the response

    Returns:
        json: response
    """
    response = {}
    # Add all the records to be inserted in response
    response['insert'] = insert
    # Add all the records to be marked as deleted in response
    response['delete'] = delete
    # Add updated state to response
    response['state'] = state
    # Add schema defintion in response
    response['schema'] = get_schema()
    # Add hasMore flag
    response['hasMore'] = hasMore
    return response


def initialize_state(state):
    """This is a function to initialize state

    Args:
        state (json): State of the connector

    Returns:
        json: State of the connector
    """

    # If state is not initialized the initialize it
    if(not state):
        state["ticker_offset"] = 0
        state["ticker_start_cursor"] = "2000-01-01"
        state["ticker_end_cursor"] = str(date.today())

    # Fetch data till the latest date if ticker_offset is 0
    if(state["ticker_offset"] == 0):
        state["ticker_end_cursor"] = str(date.today())
    return state


def get_schema():
    """This is a function to get schema

    Returns:
        json: schema
    """
    tickersSchema = {}
    tickersSchema['primary_key'] = ['symbol']
    tickersPriceSchema = {}
    tickersPriceSchema['primary_key'] = ['symbol', 'date']
    schema = {}
    schema['tickers'] = tickersSchema
    schema['tickers_price'] = tickersPriceSchema
    return schema
