import boto3
import datetime
import json
from datetime import date
import http.client

def lambda_handler(request, context):

    # Fetch records using api calls
    (insert, delete, state, hasMore) = api_response(request['state'], request['secrets'])

    followerSchema = {}
    followerSchema['primary_key'] = ['user_id']

    tweetSchema={}
    tweetSchema['primary_key'] = ['tweet_id']

    schema = {}
    schema['followers']=followerSchema
    schema['tweets']=tweetSchema

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
    response['hasMore'] = hasMore

    # Store the data in s3 file
    json_str = bytes(json.dumps(response).encode("utf-8"))
    push_data_s3(request, json_str)

    # Remove insert and delete from response
    response.pop('insert')
    response.pop('delete')
    return response

def api_response(state, secrets):
    if(state):
        next_cursor_followers = state["next_cursor_followers"]
        tweet_start_date=state["tweet_start_date"]
        tweet_end_date=state["tweet_end_date"]
        next_cursor_tweet=state["next_cursor_tweet"]
    else:
        next_cursor_followers = "0"
        tweet_start_date=str(date.today()-datetime.timedelta(days=10))
        tweet_end_date=str(date.today())
        next_cursor_tweet="0"

    insertFollowers,next_cursor_followers = get_followers(secrets['apiKey'],next_cursor_followers)

    if(tweet_end_date==str(date.today()-datetime.timedelta(days=10))):
        deleteTweetsItermediate,next_cursor_tweet=get_tweets(secrets['apiKey'],next_cursor_tweet,tweet_start_date,tweet_end_date)
        deleteTweets=[]
        for i in deleteTweetsItermediate:
            deleteTweets.append({"tweet_id":i["tweet_id"]})
        insertTweets=[]
        if(next_cursor_tweet=="-1"):
            tweet_start_date=str(date.today()-datetime.timedelta(days=10))
            tweet_end_date=str(date.today())
            next_cursor_tweet="0"
    else:
        insertTweets,next_cursor_tweet=get_tweets(secrets['apiKey'],next_cursor_tweet,tweet_start_date,tweet_end_date)
        deleteTweets=[]

    state,insert,delete,hasMore = {},{},{},False

    if(next_cursor_followers!="-1" or next_cursor_tweet!="-1"):
        hasMore=True
    else:
        next_cursor_followers, next_cursor_tweet="0","0"

    insert['followers'] = insertFollowers
    delete['followers']=[]
    state['next_cursor_followers']=next_cursor_followers

    insert['tweets'] = insertTweets
    delete['tweets'] = deleteTweets
    state['next_cursor_tweet']=next_cursor_tweet
    state["tweet_start_date"]=tweet_start_date
    state["tweet_end_date"]=tweet_end_date

    return (insert, delete, state, hasMore)


def get_followers(apiKey,next_cursor):
    if(next_cursor!="0" and next_cursor!="-1"):
        path = "/user/followers/continuation?user_id=1131570801877106689&limit=2&continuation_token="+next_cursor
        headers = {
            "X-RapidAPI-Key": apiKey,
            "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
        }

        conn = http.client.HTTPSConnection("twitter154.p.rapidapi.com")
        conn.request("GET", path, headers=headers)
        response = json.loads(conn.getresponse().read().decode("utf-8"))

        next_cursor=response["continuation_token"]
        if(not response["results"]):
            next_cursor="-1"
        return response["results"],next_cursor

    elif(next_cursor=="0"):
        path = "/user/followers?user_id=1131570801877106689&limit=2"
        headers = {
            "X-RapidAPI-Key": apiKey,
            "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
        }

        conn = http.client.HTTPSConnection("twitter154.p.rapidapi.com")
        conn.request("GET", path, headers=headers)
        response = json.loads(conn.getresponse().read().decode("utf-8"))

        next_cursor=response["continuation_token"]
        if(not response["results"]):
            next_cursor="-1"
        return response["results"],next_cursor
    else:
        return [],"-1"


def get_tweets(apiKey,next_cursor,start_date,end_date):
    if(next_cursor!="0" and next_cursor!="-1"):

        path = "/search/search/continuation?query=%23python&section=top&min_retweets=20&min_likes=20&limit=5&language=en&start_date=" + start_date+ "&end_date=" + end_date +"&continuation_token="+next_cursor
        headers = {
            "X-RapidAPI-Key": apiKey,
            "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
        }

        conn = http.client.HTTPSConnection("twitter154.p.rapidapi.com")
        conn.request("GET", path, headers=headers)
        response = json.loads(conn.getresponse().read().decode("utf-8"))

        next_cursor=response["continuation_token"]
        if(not response["results"]):
            next_cursor="-1"
        return response["results"],next_cursor
    elif(next_cursor=="0"):
        path = "/search/search?query=%23python&section=top&min_retweets=20&min_likes=20&limit=5&language=en&start_date=" + start_date+ "&end_date=" + end_date
        headers = {
            "X-RapidAPI-Key": apiKey,
            "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
        }

        conn = http.client.HTTPSConnection("twitter154.p.rapidapi.com")
        conn.request("GET", path, headers=headers)
        response = json.loads(conn.getresponse().read().decode("utf-8"))
        if(response.get("continuation_token")):
            next_cursor=response["continuation_token"]
        else:
            next_cursor="-1"
        if(response.get("results")):
            if(not response["results"]):
                next_cursor="-1"
            return response["results"],next_cursor
        else:
            return [],next_cursor
    else:
        return [],"-1"



def push_data_s3(request, json_str):
    client = boto3.client('s3')
    client.put_object(Body=json_str, Bucket=request["bucket"], Key=request["file"])
