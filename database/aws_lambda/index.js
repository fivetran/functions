/**
* create a folder then change path in the terminal/cmd to that folder and execute the command 'npm install mysql'
* create an 'index.js' file in the same folder and copy the following code in it.
* zip the folder and upload it to AWS Lambda.
*/
/**
* Following code is based on the assumption that the table structure consists of a column named 'last_modified(timestamp)' on the basis of which incremental update will happen
* and 'isDeleted(int11)' whose value defines if that particular row has been deleted or not (0 - not deleted, 1 - deleted).
*/
let mysql = require('mysql');
exports.handler = (request, context, callback) => {
    let pool = mysql.createPool({
        host: "host",
        port: "port",
        user: "user_name",
        password: "password",
        database: "db"
    });

    //prevent timeout from waiting event loop
    context.callbackWaitsForEmptyEventLoop = false;
    pool.getConnection((err, connection) => {
        // Use the connection
        let query = request.state.employee ? 'SELECT * from employee where last_modified >= "' + request.state.employee + '" order by last_modified' : 'SELECT * from employee order by last_modified';

        connection.query(query, (error, results) => {
            // And done with the connection.
            connection.release();

            // Handle error after the release.
            if (error) {
                callback(error);
            }

            let insertTransactions = [];
            let deleteTransactions = [];
            let cursor;
            results.forEach((record) => {
                /**
                * store the record as a key value pair of attribute name and attribute value
                * 'last_modified' is the column on the basis of which incremental update will happen
                * 'isDeleted' defines if the column has been deleted or not
                */
                let record = {
                    column_1: record.column_1,
                    column_2: record.column_2,
                    column_3: record.column_3,
                    isDeleted: record.isDeleted,
                    last_modified: record.last_modified
                }

                if (record.isDeleted === 0) {
                    insertTransactions.push(record);
                } else {
                    deleteTransactions.push(record);
                }
                cursor = record.last_modified
            })

            // Populate records and state
            callback(null, ({
                state: {
                    table_name: cursor
                },
                insert: {
                    table_name: insertTransactions
                },
                delete: {
                    table_name: deleteTransactions
                },
                schema: {
                    table_name: {
                        primary_key: ['primary_key'] //Enter the name of the primary key column
                    }
                },
                hasMore: false
            }))
        });
    });
};