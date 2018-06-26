const https = require('https');
const url = require('url');

exports.handler = (request, context, callback) => {
    update(request.state, request.secrets, callback);
};

function update(state, secret, callback) {
    let result = initializeState(state);
    let since = state.astroidsCursor || "2018-05-01";
    let baseApi = "https://api.nasa.gov/neo/rest/v1/feed?start_date=" + new Date(since).toISOString().slice(0,10) + "&api_key=" + secret.apiKey;
        const request = https.get(baseApi, response => {
            if (response.statusCode < 200 || response.statusCode > 299)
                callback(new Error('Request failed with code: ' + response.statusCode), null);

            // temporary data holder
            let body = "";
            response.on('data', (chunk) => body += chunk);
            response.on('end', () => {
                let insertAsteroids = [], deleteAsteroids = [];
                let jsonData = JSON.parse(body);
                let neoData = jsonData["near_earth_objects"];
                let deleted = true;
                for (var date in neoData) {
                    if (!neoData.hasOwnProperty(date))
                        continue;

                    if(deleted){
                        neoData[date].map(a => deleteAsteroids.push(flattenOneLevel(a)));
                        deleted = false;
                    } else {
                        neoData[date].map(a => insertAsteroids.push(flattenOneLevel(a)));
                    }
                    since = (new Date(date) > new Date(since)) ? date : since;
                }
                
                result.insert.astroids = insertAsteroids;
                result.delete.astroids = deleteAsteroids;
                result.state.astroidsCursor = since;
                console.log("Data fetching done");
                callback(null, result);
            });
        });
        
        request.on('error', (err) => callback(err, null));
}

function flattenOneLevel(arr) {
    var newObj = {};
    flatten("", arr, newObj, true);
    return newObj;
}

function flatten(currentKey, obj, target, nested) {
    for (var i in obj) {
        if (!obj.hasOwnProperty(i)) 
            continue;
        
        var newKey = i;
        var newVal = obj[i];

        if (currentKey.length > 0) 
            newKey = currentKey + '_' + i;

        if (nested && typeof newVal === "object") 
            flatten(newKey, newVal, target, false);
        else
            target[newKey] = newVal;
    }
}

function initializeState(state) {
    return {
        state: {...state},
        insert: {
            "astroids": []
        },
        delete: {
            "astroids": []
        },
        schema : {
            "astroids" : {
                primary_key : ['neo_reference_id']
            }
        },
        hasMore : false
    };
}