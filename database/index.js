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
    let query = "";
    if (!request.state.table_name) {
      query = 'SELECT * from table_name order by last_modified';
    } else {
      query = 'SELECT * from table_name where last_modified >= "' + request.state.table_name + '" order by last_modified';
    }

    connection.query(query, (error, results) => {
      // And done with the connection.
      connection.release();
      // Handle error after the release.
      if (error) {
        callback(error);
      }
      else {
        let insertTransactions = [];
        let deleteTransactions = [];
        let cursor;
        for (i in results) {
          /**
          * store the record as a key value pair of attribute name and attribute value
          * 'last_modified' is the column on the basis of which incremental update will happen
          * 'isDeleted' defines if the column has been deleted or not
          */
          let record = { column_1: results[i].column_1, column_2: results[i].column_2, column_3: results[i].column_3, isDeleted: results[i].isDeleted, last_modified: results[i].last_modified }

          if (results[i].isDeleted === 0) {
            insertTransactions.push(record);
          }
          else {
            deleteTransactions.push(record);
          }
          cursor = record.last_modified
        }
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
      }
    });
  });
};