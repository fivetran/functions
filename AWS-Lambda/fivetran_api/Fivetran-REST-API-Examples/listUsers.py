# listUsers
# Returns a list of all users within your Fivetran account.

# Reference: https://fivetran.com/docs/rest-api/users#listallusers

import fivetran_api

# Fivetran API URL (users endpoint)
url = "https://api.fivetran.com/v1/users"

fivetran_api.dump(fivetran_api.get_url(url))
