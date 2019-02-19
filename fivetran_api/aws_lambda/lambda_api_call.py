import datetime
import json
import requests
import time


def lambda_handler(request, context):

    # Fivetran API URL
    url = "http://api.fivetran.com/v1/groups/{group_id}/connectors".format(group_id=request['GROUP_ID'])

    # Make a request to the endpoint using the correct auth values
    auth_values = (request['API_KEY'], request['API_SECRET'])
    response = requests.get(url, auth=auth_values)

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    # Convert JSON to dict
    response_json = response.json()
    item_list = response_json['data']['items']

    # These will be put into "insert" in the response
    result_items = []
    result_tasks = []
    result_warnings = []

    # Iterate through the items returned by the API
    for entry in item_list:
        entry_item = {}
        entry_tasks = []
        entry_warnings = []
        for k, v in entry.items():
            if k != "status":
                entry_item[k] = v
            elif k == "status":

                for sub_key in ["sync_state", "setup_state", "is_historical_sync", "update_state"]:
                    entry_item[sub_key] = v[sub_key]

                for task in v['tasks']:
                    entry_tasks.append({"id": entry['id'],
                                        "message": task['message'],
                                        "code": task['code']})
                for warning in v['warnings']:
                    entry_warnings.append({"id": entry['id'],
                                           "message": warning['message'],
                                           "code": warning['code']})
        result_items.append(entry_item)
        result_tasks.extend(entry_tasks)
        result_warnings.extend(entry_warnings)

    result = dict()
    result['state'] = {timestamp: timestamp}
    result['insert'] = {"items": result_items,
                        "tasks": result_tasks,
                        "warnings": result_warnings}

    print(json.dumps(result))
    return json.dumps(result)

