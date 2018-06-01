/*
This lambda function fetched search results from elastic search instance

Request parameter has two nodes, state and secret.
`state` node is empty for the first request. In this lambda function, cursor for entity `search` is stored in `state` object.
`secrets` node contains the host name of elastic search instance 
{
    "state" : {},
    "secrets" : {
        "host" : "host_name"
    }
}

Insert node contains records fetched using search query `bag`.
Delete node contains records fetched using search query `puma`.

Primary key for the records are [_id, _index, _type, sync_time]
*/
var RecordOperation = {
    INSERT : 1,
    DELETE : 2
}

exports.handler = (request, context, callback) => {
    update(request.state, request.secrets, callback)
}

async function update(state, secrets, callback) {
    let response = initializeResponse(state);
     
    let insertResponse = fetchSearchResult(state, secrets, 'products', 'product', 'Bag');
    let deleteResponse = fetchSearchResult(state, secrets, 'products', 'product', 'Puma');
    
    insertResponse.then(function(searchResult) {
        putSearchResult(response, searchResult, RecordOperation.INSERT)
    }).catch(function (err) {
        callback(err); 
    });
    
    deleteResponse.then(function(searchResult) {
        putSearchResult(response, searchResult, RecordOperation.DELETE)
    }).catch(function (err) {
        callback(err); 
    });
    
    await insertResponse;
    await deleteResponse;
    
    response.state = {
        "search" : new Date()
    }
    
    callback(null, response);
}

function initializeResponse(state) {
    return {
        "state": {...state}, 
        "insert": {
            "search": []
        },
        "delete": {
            "search": []
        },
        "schema": {
            "search": {
                "primary_key": ['_id', '_index', '_type', 'sync_time']
            }
        },
        hasMore: false
    };
}

function fetchSearchResult(state, secrets, indexName, type, query) {
    let elasticsearch = require('elasticsearch');
    
    let client = new elasticsearch.Client({
  	    host: secrets.host,
  	    log: 'trace'
    });
    
    let a = client.search({
        index: indexName,
        type: type,
        q: query
    });
    
    return a;
}

function putSearchResult(response, searchResult, recordOperation) {
    let index;
    
    let hits = searchResult.hits.hits;
    
    for(index = 0; index < hits.length; index++) {
        let keys = Object.keys(hits[index]);
        
        let keyIndex;
        let result = {};
        
        for(keyIndex = 0; keyIndex < keys.length; keyIndex++) {
            let key = keys[keyIndex];
            
            if(hits[index][key] instanceof Object) {
                putNestedObject(result, key, hits[index][key]);
                continue;
            }
            
            result[key] = hits[index][key];
        }
        
        result['sync_time'] = new Date();
        
        if (recordOperation == RecordOperation.INSERT) {
            response.insert.search.push(result);
        } else {
            response.delete.search.push(result);
        }
    }
    
    return response;
}

function putNestedObject(result, prefix, object) {
    let keys = Object.keys(object);
    let keyIndex;
    
    for(keyIndex = 0; keyIndex < keys.length; keyIndex++) {
        let key = keys[keyIndex];
        
        result[prefix + key] = object[key];
    }
}

