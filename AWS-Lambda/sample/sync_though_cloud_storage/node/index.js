exports.handler = (request, context, callback) => {
    callback(null, update(request.state, request.secrets,request.bucket,request.file));
};
function update(state, secrets,bucket,key) {
    // Fetch records using api calls
    let [insertTransactions, deleteTransactions, newTransactionsCursor] = apiResponse(state, secrets);

    // Populate insert and delete in records
    var records=JSON.stringify({
        insert: {
            transactions: insertTransactions
        },
        delete: {
            transactions: deleteTransactions
        }
    })

    // Store records in s3 bucket
    putObjectToS3(bucket,key,records)

    // Return response
    return ({
        state: {
            transactionsCursor: newTransactionsCursor
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

// Function to store data in s3 bucket
var AWS = require('aws-sdk');
function putObjectToS3(bucket, key, data){
    var s3 = new AWS.S3();
        var params = {
            Bucket : bucket,
            Key : key,
            Body : data
        }
        s3.putObject(params, function(err, data) {
          if (err) console.log(err, err.stack); // an error occurred
          else     console.log(data);           // successful response
        });
}