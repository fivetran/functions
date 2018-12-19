from datetime import datetime, date
from time import time, struct_time, mktime
import boto3
import csv
import decimal
import json
import pg8000


# Connect via pg8000
def get_connection(database, host, port, user, password):
    conn = None
    try:
        conn = pg8000.connect(database=database, host=host, port=port, user=user, password=password, ssl=True)
    except Exception as err:
        print(err)
    return conn


# Handle data types such as datetime and decimal
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


# Write a log file containing your save state to S3
def write_log_s3(cursor_row, client, bucket_name, key_cursor_file):
        output = {
            "timestamp": datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S'),
            "cursor": cursor_row
        }
        client.put_object(Body=json.dumps(output), Bucket=bucket_name, Key=key_cursor_file)


# Handler function
def lambda_handler(event, context):
    # 1. Import AWS and database credentials from a separate file
    with open("aws_credentials/credentials.csv") as credentials:
        reader = list(csv.DictReader(credentials))
        access_key_id = reader[0]['Access key ID']
        aws_secret_access_key = reader[0]['Secret access key']
        dbname = reader[0]['dbname']
        host = reader[0]['host']
        port = int(reader[0]['port'])
        user = reader[0]['user']
        password = reader[0]['password']

    # 2. Access S3; Instantiate some boto3 objects so that you can see what's in S3
    client = boto3.client('s3',
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=aws_secret_access_key
                          )

    resource = boto3.resource('s3',
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=aws_secret_access_key
                              )

    # You will obviously need to substitute your own bucket and file names
    bucket_name = "short-redshift-migration"
    key_cursor_file = "test_logs/log.json"
    bucket = resource.Bucket(bucket_name)

    # 3. Connect to Redshift
    con = get_connection(dbname, host, port, user, password)
    cur = con.cursor()

    # Make sure you should know these details about the table you are migrating beforehand
    # Set the "limit" according to your estimates of the table's size and row count
    table = "sales"
    primary_key = "salesid"
    cursor = "saletime"
    limit = 50

    # 4. Query redshift; check for the existence of your save state
    if key_cursor_file in [item.key for item in bucket.objects.all()]:

        cursor_object = client.get_object(Bucket=bucket_name, Key=key_cursor_file)['Body']
        cursor_value = json.load(cursor_object)['cursor']
        cur.execute("SELECT * FROM {table} WHERE {cursor} > '{cursor_value}' ORDER BY {cursor} LIMIT {limit}".format(
            cursor_value=cursor_value, cursor=cursor, limit=limit, table=table))
    else:
        cur.execute("SELECT * FROM {table} ORDER BY {cursor} LIMIT {limit}".format(cursor=cursor, limit=limit,
                                                                                   table=table))

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
        row_data = {}
        for numb in range(len(columns)):
            row_data[columns[numb]] = encode_json(row[numb])
        response['insert'][table].append(row_data)

    response['state'] = response['insert'][table][-1][cursor]
    response['schema'] = {table: {"primary_key": [primary_key]}}
    response['hasMore'] = False

    # Write the save state to S3
    write_log_s3(response['insert'][table][-1][cursor], client, bucket_name, key_cursor_file)

    return response
