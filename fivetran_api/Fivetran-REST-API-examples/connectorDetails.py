# connectorDetails
# Returns a connector object if a valid identifier was provided.

# Reference: https://fivetran.com/docs/rest-api/connectors#retrieveconnectordetails

import fivetran_api

# Fivetran API URL (Replace {connector_id} with a valid connector id).
url = "https://api.fivetran.com/v1/connectors/{connector_id}"

fivetran_api.dump(fivetran_api.get_url(url))