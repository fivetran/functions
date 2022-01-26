import logging
import json
import requests
import azure.functions as func


### LONDON TUBE EXAMPLE ###

def main(req: func.HttpRequest) -> func.HttpResponse:

    result = requests.get('https://api.tfl.gov.uk/line/mode/tube/status',headers={"content-type":"application/json", "charset":"utf-8"})


    since_id = None
    timeline = json.loads(result.text)


    # Reformat Twitter's response into nice, flat tables
    tflLineStatus = []
    for t in timeline:
        # Remember the first id we encounter, which is the most recent
        if (since_id == None) :
            since_id = t["id"]

        # Add all tflLineStatus
        tflLineStatus.append({
            "linename": t["id"],
            "linestatus": t["lineStatuses"][0]["statusSeverityDescription"],
            "timestamp" : t["created"]
        })
    
    # Send JSON response back to Fivetran

    if(since_id==None):
        since_id = req.state.since_id
    
    ## Expexted Response by Fivetran ## 
    ans = {
        # // Remember the most recent id, so our requests are incremental
        "state": {
            since_id: since_id
        },
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


    
    # HttpResponse only takes str, bytes or bytearray as body
    # Convert Json or Dict into supppotted format.
    return func.HttpResponse(
             json.dumps(ans,indent=4),
             mimetype='application/json',
             status_code=200
        )
