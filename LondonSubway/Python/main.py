import json
import requests

def lambda_handler(req):
    result = requests.get('https://api.tfl.gov.uk/line/mode/tube/status',headers={"content-type":"application/json", "charset":"utf-8"})


    since_id = None
    # print(json.loads(result.text))
    timeline = json.loads(result.text)


        #  Reformat Twitter's response into nice, flat tables
    tflLineStatus = []
    for t in timeline:
        # // Remember the first id we encounter, which is the most recent
        if (since_id == None) :
            since_id = t["id"]
        

        # console.log(`Selecting the schema values`);

        # // Add all tflLineStatus
        tflLineStatus.append({
            "linename": t["id"],
            "linestatus": t["lineStatuses"][0]["statusSeverityDescription"],
            "timestamp" : t["created"]
        })
    
    # // Send JSON response back to Fivetran


    ans = {
        # // Remember the most recent id, so our requests are incremental
        "state": {
            # since_id: since_id == null ? req.state.since_id : since_id
        },
        # // Fivetran will use these primary keys to perform a `merge` operation,
        # // so even if we send the same row twice, we'll only get one copy in the warehouse
        "schema" : {
            "tflLineStatus" : {
                "primary_key" : ["linename"]
            }
        },
        "insert": {
            "tflLineStatus": tflLineStatus
        },
        "hasMore" : False
    }
    return ans;
