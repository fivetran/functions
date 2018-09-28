import json
import requests


def make_request(url, api_key):
    # DISCLAIMER - PASSING AN API KEY DIRECTLY INTO AN HTTP REQUEST CAN BE CONSIDERED BAD PRACTICE
    # IN PRODUCTION YOU MIGHT WANT TO ENCRYPT YOUR KEY
    headers = {"Authorization": "Bearer {0}".format(api_key)}
    r = requests.get(url, headers=headers)
    return json.loads(r.text)


def assemble_response_json(insert, state):
    response_dict = {
        "state": state,
        "schema": {
            "businesses": {
                "primary_key": [
                    "id"
                ]
            },
            "categories": {
                "primary_key": [
                    "alias"
                ]
            },
            "business_category": {
            }
        },
        "insert": insert,
        "hasMore": False
    }
    return json.dumps(response_dict)


def handler(request):

    root_url = "https://api.yelp.com/v3/businesses/search"
    location = "San+Francisco"
    type = "makerspaces"

    # GET THE CREDENTIALS FROM THE TRIGGERING EVENT
    request_json = request.get_json()
    api_key = request_json['secrets']['api_key']

    url = "{0}?location={1}&categories={2}".format(root_url, location, type)

    # REQUEST DATA FROM API
    response_text = make_request(url, api_key)

    # ITERATE THROUGH LIST OF BUSINESSES
    results = response_text['businesses']

    business_table = []
    category_table = []
    bus_cat_join_table = []

    for result in results:
        result.pop("transactions", None)

        categories = result.pop("categories", None)

        # UN-NEST SOME OF THE KEYS
        location = result.pop("location", None)
        result.update(location)

        coordinates = result.pop("coordinates", None)
        result.update(coordinates)

        # BUILD LISTS FOR EACH TABLE
        business_table.append(result)

        for category in categories:
            category_table.append(category)

            bus_cat = category.copy()
            bus_cat['id'] = result['id']
            bus_cat.pop("title")
            bus_cat_join_table.append(bus_cat)

    # ASSEMBLE THE TABLES FOR INSERT
    state = business_table[-1]['id']
    insert = {
            "businesses": business_table,
            "categories": category_table,
            "business_category": bus_cat_join_table
        }

    return assemble_response_json(insert, state), 200, {"Content-Type": "application/json"}
