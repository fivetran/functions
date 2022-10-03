# createConnector
# Creates a new connector within a specified group in your Fivetran account. Runs setup tests and returns testing results.

# Reference: https://fivetran.com/docs/rest-api/connectors#createaconnector

import fivetran_api

# Fivetran API URL 
url = "https://api.fivetran.com/v1/connectors/"
#Connector Configuration (replace {group_id} with your group id)
config_values = {
    "service": "criteo",
    "group_id": "{group_id}",
    "trust_certificates": "true",
    "config": {
        "schema": "criteo",
        "username": "myuser",
        "password": "mypassword",
        "app_token": "myapptoken"
    }
}

fivetran_api.dump(fivetran_api.post_url(url, config_values))
