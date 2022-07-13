import json
import boto3

def lambda_handler(request, context):
    # Fetch records using api calls
    (insertTransactions, deleteTransactions, newTransactionCursor) = api_response(request['state'], request['secrets'])
    # Populate records in insert
    insert = {}
    insert['transactions'] = insertTransactions
    delete = {}
    delete['transactions'] = deleteTransactions
    state = {}
    state['transactionsCursor'] = newTransactionCursor
    transactionsSchema = {}
    transactionsSchema['primary_key'] = ['order_id', 'date']
    schema = {}
    schema['transactions'] = transactionsSchema
    response = {}
    # Add updated state to response
    response['state'] =  state
    # Add all the records to be inserted in response
    response['schema'] = schema
    # Add hasMore flag
    response['hasMore'] = 'false'

    response_s3={}
    # Add all the records to be inserted in response_s3
    response_s3['insert'] = insert
    # Add all the records to be marked as deleted in response_s3
    response_s3['delete'] = delete

    json_str = bytes(json.dumps(response_s3).encode("utf-8"))

    # Push data in s3
    push_data_s3(request, json_str)

    return response

def api_response(state, secrets):
    # your api call goes here
    insertTransactions = [
            {"date":'2017-12-31T05:12:05Z', "order_id":1001, "amount":'$1200', "discount":'$12'},
            {"date":'2017-12-31T06:12:04Z', "order_id":1001, "amount":'$1200', "discount":'$12'},
    ]
    deleteTransactions = [
            {"date":'2017-12-31T05:12:05Z', "order_id":1000, "amount":'$1200', "discount":'$12'},
            {"date":'2017-12-31T06:12:04Z', "order_id":1000, "amount":'$1200', "discount":'$12'},
    ]
    return (insertTransactions, deleteTransactions, '2018-01-01T00:00:00Z')

#Function to store data in s3
def push_data_s3(request, json_str):
    client = boto3.client('s3')
    client.put_object(Body=json_str, Bucket=request["bucket"], Key=request["file"])