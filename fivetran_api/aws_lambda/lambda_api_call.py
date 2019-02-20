import datetime
from botocore.vendored import requests
import time


def lambda_handler(request, context):

    # Fivetran API URL
    api_key = request['secrets']['api_key']
    group_id = request['secrets']['group_id']
    api_secret = request['secrets']['api_secret']

    url = 'http://api.fivetran.com/v1/groups/{group_id}/connectors'.format(group_id=group_id)

    # Make a request to the endpoint using the correct auth values

    auth_values = (api_key, api_secret)
    response = requests.request('GET', url, auth=auth_values)

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    # Convert JSON to dict
    response_json = response.json()
    item_list = response_json['data']['items']

    # These will be put into 'insert' in the response
    result_items = []
    result_tasks = []
    result_warnings = []

    # Iterate through the items returned by the API
    for entry in item_list:
        entry_item = {}
        entry_tasks = []
        entry_warnings = []
        for k, v in entry.items():
            if k != 'status':
                entry_item[k] = v
            else:

                for sub_key in ['sync_state', 'setup_state', 'is_historical_sync', 'update_state']:
                    entry_item[sub_key] = v[sub_key]

                for task in v['tasks']:
                    entry_tasks.append({'id': entry['id'],
                                        'message': task['message'],
                                        'code': task['code']})
                for warning in v['warnings']:
                    entry_warnings.append({'id': entry['id'],
                                           'message': warning['message'],
                                           'code': warning['code']})
        result_items.append(entry_item)
        result_tasks.extend(entry_tasks)
        result_warnings.extend(entry_warnings)

    result = {}
    result['state'] = {timestamp: timestamp}
    result['insert'] = {'items': result_items,
                        'tasks': result_tasks,
                        'warnings': result_warnings}

    return result

