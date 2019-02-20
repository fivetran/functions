from datetime import datetime, date
from time import struct_time, mktime
import decimal
import pg8000


# Connect via pg8000
def get_connection(database, host, port, user, password):
    conn = None
    try:
        conn = pg8000.connect(database=database, host=host, port=port, user=user, password=password, ssl=True)
    except Exception as err:
        print(err)
    return conn


# Handle Python data types such as datetime and decimal
def encode_json(data):
    if isinstance(data, datetime):
        return str(data)
    if isinstance(data, date):
        return str(data)
    if isinstance(data, decimal.Decimal):
        return float(data)
    if isinstance(data, struct_time):
        return datetime.fromtimestamp(mktime(data))
    return data


# Handler function
def lambda_handler(request, context):
    # 1. Import AWS and database credentials
    # These and other parameters should be wrapped up in "request," which is relayed from the connector's "secrets"
    dbname = request['secrets']['dbname']
    host = request['secrets']['host']
    port = int(request['secrets']['port'])
    user = request['secrets']['user']
    password = request['secrets']['password']

    # 2. Set state
    try:
        cursor_value = request['state']['cursor']
    except KeyError:
        cursor_value = "1970-01-01T00:00:00"

    # 3. Connect to Redshift
    con = get_connection(dbname, host, port, user, password)
    cur = con.cursor()

    # Make sure you should know these details about the table you are migrating beforehand
    # Set the "limit" according to your estimates of the table's size and row count
    # Again, these can also be stored in "request"
    table = request['secrets']["table"]
    primary_key = request['secrets']["primary_key"]
    cursor = request['secrets']["cursor"]
    limit = request['secrets']["limit"]

    # 4. Query redshift; check for the existence of your save state
    cur.execute("SELECT * FROM {table} WHERE {cursor} > '{cursor_value}' ORDER BY {cursor} LIMIT {limit}".format(
            cursor_value=cursor_value, cursor=cursor, limit=limit, table=table))

    # Get column names
    columns = [item[0].decode() for item in cur.description]

    # Get data
    output_data = cur.fetchall()

    # Handle exception; stop once you reach the end of the table. Avoids "out of index" error on line 113
    if len(output_data) == 0:
        return {}

    # 5. Generate a JSON response
    response = dict()
    response['insert'] = {table: []}

    for row in output_data:
        serialized_row = [encode_json(item) for item in row]
        row_data = dict(zip(columns, serialized_row))
        response['insert'][table].append(row_data)

    response['state'] = request['state'] if len(output_data) == 0 else {"cursor": response['insert'][table][-1][cursor]}
    response['schema'] = {table: {"primary_key": [primary_key]}}
    response['hasMore'] = False if len(output_data) < limit else True

    print(response)

    return response
