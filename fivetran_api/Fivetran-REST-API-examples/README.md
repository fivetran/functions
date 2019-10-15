# Fivetran REST API Examples

In addition to managing your Fivetran account using the dashboard, you can now perform key management actions such as creating and managing new users and creating and managing connectors using the Fivetran REST API.

To get you started, we've provided several example python scripts to cover common API use cases.

## Config

1. Use the [Getting Started guide](https://fivetran.com/docs/rest-api/getting-started) to retrieve your API Key and API Secret.
2. In `config.py`, replace the `API_KEY` and `API_SECRET` values with your API Key and API Secret.

## Usage

Call the desired python script from your external code or terminal, making sure to add your `group_id` or `connector_id` to the script where appropriate.

Example: `python createConnector.py`

## Included Examples

### connectorDetails

Returns a connector object if a valid identifier was provided.

Reference: https://fivetran.com/docs/rest-api/connectors#retrieveconnectordetails

### createConnector

Creates a new connector within a specified group in your Fivetran account. Runs setup tests and returns testing results.

Reference: https://fivetran.com/docs/rest-api/connectors#createaconnector

### createFTPConnector

Identical to createConnector, with the addition of advanced field configuration available to file connectors.

Reference: https://fivetran.com/docs/rest-api/connectors/config#ftp

### listGroupConnectors

Returns a list of information about all connectors within a group in your Fivetran account.

Reference: https://fivetran.com/docs/rest-api/groups#listallconnectorswithinagroup

### listGroups

List all Fivetran groups available to the authenticated Fivetran User.

Reference: https://fivetran.com/docs/rest-api/groups

### listUsers

Returns a list of all users within your Fivetran account.

Reference: https://fivetran.com/docs/rest-api/users#listallusers
