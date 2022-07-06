import boto3
import datetime
import json
from datetime import date
from botocore.vendored import requests

def lambda_handler(request, context):
    # Fetch records using api calls
    (insertRecords, deleteRecords, state) = api_response(request['state'], request['secrets'])
    # Populate records in insert
    insert = {}
    insert['weatherInformation'] = insertRecords
    # Populate records in delete
    delete = {}
    delete['weatherInformation']=deleteRecords
    # Populate schema
    weatherSchema = {}
    weatherSchema['primary_key'] = ['date']
    schema = {}
    schema['weatherInformation'] = weatherSchema

    response = {}
    # Add updated state to response
    response['state'] =  state
    # Add all the records to be inserted in response
    response['insert'] = insert
    # Add all the records to be marked as deleted in response
    response['delete'] = delete
    # Add schema defintion in response
    response['schema'] = schema
    # Add hasMore flag
    response['hasMore'] = 'false'

    # Store the data in s3 file
    json_str = bytes(json.dumps(response).encode("utf-8"))
    push_data_s3(request, json_str)

    # Remove insert and delete from response
    response.pop('insert')
    response.pop('delete')
    return response


def api_response(state, secrets):

    if(state):
        syncStartDate=state['lastSyncDate']
    else:
        syncStartDate= date.today()

    syncEndDate=date.today()
    if(str(syncStartDate)<=str(syncEndDate)):
        url = "https://weatherapi-com.p.rapidapi.com/history.json"
        querystring = {"q":"London","dt":str(syncStartDate),"lang":"en","end_dt":str(syncEndDate)}
        headers = {
            "X-RapidAPI-Key": secrets['apiKey'],
            "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring).json()
        intermediateResult=response["forecast"]["forecastday"]
        finalList=[]
        for values in intermediateResult:
            tempDict=values['day']
            tempDict['date']=values['date']
            finalList.append(tempDict)

        insertRecords=finalList
        deleteRecords = []
        state['lastSyncDate']=str(syncEndDate+datetime.timedelta(days=1))
        return (insertRecords, deleteRecords,state)


def push_data_s3(request, json_str):
    client = boto3.client('s3')
    client.put_object(Body=json_str, Bucket=request["bucket"], Key=request["file"])
