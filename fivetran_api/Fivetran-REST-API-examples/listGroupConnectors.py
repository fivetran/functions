# listGroupConnectors
# Returns a list of information about all connectors within a group in your Fivetran account.

# Reference: https://fivetran.com/docs/rest-api/groups#listallconnectorswithinagroup

import fivetran_api

# Fivetran API URL (replace {group_id} with your group id)
url = "https://api.fivetran.com/v1/groups/{group_id}/connectors"

fivetran_api.dump(fivetran_api.get_url(url))
