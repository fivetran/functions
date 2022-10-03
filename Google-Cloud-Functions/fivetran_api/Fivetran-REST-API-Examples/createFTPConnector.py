# createFTPConnector
# Identical to createConnector, with the addition of advanced field configuration available to file connectors.

# Reference: https://fivetran.com/docs/rest-api/connectors/config#ftp

import fivetran_api

# Fivetran API URL 
url = "https://api.fivetran.com/v1/connectors/"
#Connector Configuration (replace {group_id} with your group id)
config_values = {
    "service": "ftp",
    "group_id": "{group_id}",
    "config": {
        "schema": "schema_name",
        "table": "table_name",
        "host": "ftp.company.com",
        "port": "21",
        "user": "user_name",
        "password": "password",
        "isSecure": "false",
        "prefix": "folder_path",
        "pattern": "file_pattern",
        "fileType": "infer",
        "compression": "infer",
        "onError": "skip",
        "appendFileOption": "upsert_file",
        "archivePattern": "regex_pattern",
        "nullSequence": "",
        "delimiter": "",
        "escapeChar": "",
        "skipBefore": "0",
        "skipAfter": "0"
    }
}

fivetran_api.dump(fivetran_api.post_url(url, config_values))
