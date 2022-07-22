import json
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
    response['insert'] = insert
    # Add all the records to be marked as deleted in response
    response['delete'] = delete
    # Add schema defintion in response
    response['schema'] = schema
    # Add hasMore flag
    response['hasMore'] = False
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
    newTransactionCursor='2018-01-01T00:00:00Z'
    return (insertTransactions, deleteTransactions, newTransactionCursor)