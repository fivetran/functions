exports.handler = (request, context, callback) => {
    callback(null, update(request.state, request.secrets));
};
function update(state, secrets) {
    // Fetch records using api calls
    let [insertTransactions, deleteTransactions, newTransactionsCursor] = apiResponse(state, secrets);
    // Populate records and state
    return ({
        state: {
            transactionsCursor: newTransactionsCursor
        },
        insert: {
            transactions: insertTransactions
        },
        delete: {
            transactions: deleteTransactions
        },
        schema : {
            transactions : {
                primary_key : ['order_id', 'date']
            }
        },
        hasMore : false
    });
}
function apiResponse(state, secrets) {
    var insertTransactions = [
            {"date":'2017-12-31T05:12:05Z', "order_id":1001, "amount":'$1200', "discount":'$12'},
            {"date":'2017-12-31T06:12:04Z', "order_id":1001, "amount":'$1200', "discount":'$12'},
    ];
    var deleteTransactions = [
            {"date":'2017-12-31T05:12:05Z', "order_id":1000, "amount":'$1200', "discount":'$12'},
            {"date":'2017-12-31T06:12:04Z', "order_id":1000, "amount":'$1200', "discount":'$12'},
    ];
    return [insertTransactions, deleteTransactions, '2018-01-01T00:00:00Z'];
}