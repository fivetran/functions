# listGroups
# List all Fivetran groups available to the authenticated Fivetran User.

# Reference: https://fivetran.com/docs/rest-api/groups

import fivetran_api

url = "https://api.fivetran.com/v1/groups"

fivetran_api.dump(fivetran_api.get_url(url))
