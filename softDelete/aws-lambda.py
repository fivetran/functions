import json
import boto3
import random
def lambda_handler(request, context):
    # Fetch records using api calls
    (insertTransactions, deleteTransactions,softDelete,newTransactionCursor) = api_response(request['state'], request['secrets'])
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

    # Add all the records to be inserted in response
    response['insert'] = insert
    # Add all the records to be marked as deleted in response
    response['delete'] = delete
    #Add all the tables to be soft Deleted in softDelete
    response['softDelete']=softDelete

    return response

def api_response(state, secrets):
    # your api call goes here
    insertTransactions = [
            {"date":'2017-12-31T06:12:04Z', "amount":'$1200', "discount":'$13'},
            {"date":'2017-12-31T06:12:04Z', "amount":'$1200', "discount":'$13'}
    ]
    #adding random order_id(primary key) to each records to make each record unique, so that we can test softDelete functionality
    for each in insertTransactions:
        each["order_id"]=random.randrange(100)
    deleteTransactions = [

    ]
    softDelete=['transactions']
    return (insertTransactions, deleteTransactions,softDelete,'2018-01-01T00:00:00Z')