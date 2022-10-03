'use strict';

const AWS = require('aws-sdk');
const s3 = new AWS.S3();

const bucketName = "lambda-function-records";
const bucketParams = { Bucket: bucketName };

const limitNumberOfFilesToUpdateInOneRun = 2;

exports.handler = (request, context, callback) => {
    update(request.state, request.secrets, callback);
};

async function update(state, secrets, callback) {
    let response = initializeResponse(state);

    let modifiedFiles = [];

    await s3.listObjects(bucketParams).promise().then(result => {
        for (let content of result.Contents) {
            // Only JSON files to be processed
            // We can add some pattern
            if (!content.Key.endsWith(".json") || Date.parse(content.LastModified) <= Date.parse(state.since)) {
                continue;
            }

            modifiedFiles.push(content);

            // If we want to process limited number of files in one lambda execution, so we should only add those number of files
            if (modifiedFiles.length === limitNumberOfFilesToUpdateInOneRun) {
                response.hasMore = true;
                break;
            }
        }
    }).catch(err => {
        callback(err); // Return when some error occurred while listing objects in bucket
        console.log("Error in listing bucket", JSON.stringify(err) + "\n");
    });

    // Sort in ascending order
    modifiedFiles.sort((a, b) => (a.LastModified > b.LastModified) ? 1 : ((b.LastModified > a.LastModified) ? -1 : 0));

    // Process files one by one
    for (let modifiedFile of modifiedFiles) {
        let params = {
            Bucket: bucketName,
            Key: modifiedFile.Key
        };

        await s3.getObject(params).promise().then(result => {
            let fileData = JSON.parse(result.Body.toString("utf-8"));

            // Deletes are save in file ending with _delete.json, otherwise file will contain records
            if (modifiedFile.Key.endsWith("_delete.json")) {
                fileData.deletes.forEach(d => response.delete.near_earth_objects.push(d));
            } else {
                let keys = Object.keys(fileData.near_earth_objects);

                keys.forEach(key => {
                    fileData.near_earth_objects[key].forEach(
                        data => {
                            data['date'] = key;
                            response.insert.near_earth_objects.push(data);
                        }
                    );
                });
            }
        }).catch(err => {
            callback(err); // Return when some error occurred while reading any file
            console.log("Error in getting object : " + err + "\n");
        });

        // Save last modified of processed file so we process files after that in next run
        response.state.since = modifiedFile.LastModified;
    }

    // Once response in generated use callback to finish lambda execution with response
    callback(null, response);
}

function initializeResponse(state) {
    // Don't assign the value directly, it means you are assigning as a reference, 
    // Now state of response doesn't get affected when change state variable in method
    return {
        state: { ...state },
        insert: {
            near_earth_objects: []
        },
        "delete": {
            near_earth_objects: []
        },
        schema: {
            near_earth_objects: {
                primary_key: ["neo_reference_id"]
            }
        },
        hasMore: false
    };
}