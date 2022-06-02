import requests
from datetime import datetime,timezone

def get_request(query, apiKey, apiUrl):
    headers = {"Authorization" : apiKey}
    response = requests.post(url=apiUrl, json={'query' : query}, headers=headers)
    if response.status_code == 200:
        response = response.json()
        return response["data"]
    else:
        return {}

def build_response(data, limit, cursor_value):
    response = dict()
    
    response['insert'] = {"boards": []} # If we had more endpoints we could add them here
    # and we would need to add them to the 'insert' section of the response below
    for row in data:
        response['insert']["boards"].append(row) 
    
    response['state'] = {'cursor': cursor_value} if len(data) == 0 else {'cursor': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")}
    response['schema'] = {"boards": {'primary_key': ["id"]}} # If we had more endpoints, we would need to add the schemas / primary keys here as well
    response['hasMore'] = False if len(data) < limit else True
    return response

def lambda_handler(request):
    # Get json from request
    request = request.get_json() 
    # Note that get_json above is a flask function, which seems to work because google cloud functions are run
    # in a flask based environment, even though we didn't import it explicitly or add it to requirements.txt

    # Import credentials
    # These and other parameters should be wrapped up in 'request,' which is relayed from the connector's 'secrets'
    apiKey = request['secrets']['apiKey']

    # Set state
    try:
        cursor_value = request['state']['cursor']
    except KeyError:
        cursor_value = '1970-01-01T00:00:00'

    # Set the 'limit' according to your estimates of the table's size and row count
    # Again, these can also be stored in 'request'
    limit = request['secrets']['limit']

    # Get data
    apiUrl = "https://api.monday.com/v2"
    boards_query = '{ boards {id name state board_folder_id } }'
    boards_data = get_request(boards_query, apiKey=apiKey, apiUrl=apiUrl)

    if len(boards_data) == 0:
        return {}

    response = build_response(boards_data["boards"], limit, cursor_value)

    print(response)

    return response
