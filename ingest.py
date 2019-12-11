import os
import requests
import json
from pprint import pprint
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth

from redis import Redis
import redis, socket, os

import argparse

# process command line arguments
parser = argparse.ArgumentParser(description="Program to ingest twitter feed into a Redis Stream")
parser.add_argument("-s", "--server", help="Redis endpoint hostname",required=True)
parser.add_argument("-p", "--port", type=int, help="Redis endpoint port",required=True)
parser.add_argument("-w", "--password", help="Redis DB password",required=False)
args = parser.parse_args()

# Construct a Redis client
host = args.server
port = args.port
password = args.password
redis_client = redis.Redis(
    host=host,
    port=port,
    password=password,
    decode_responses=True )

try :
    consumer_key = redis_client.get('consumer_key')
    consumer_secret = redis_client.get('consumer_secret')
except redis.exceptions.ConnectionError :
    print("Can't connect to Redis DB at: " + host + ":" + str(port))
    os._exit(1)
except :
    print("GET twitter credentials from Redis failed")
    os._exit(2)

stream_url = "https://api.twitter.com/labs/1/tweets/stream/sample?user.format=detailed"
#user_url = "https://api.twitter.com/1.1/users/show.json?user_id="

# Gets a bearer token
class BearerTokenAuth(AuthBase):
    def __init__(self, consumer_key, consumer_secret):
        self.bearer_token_url = "https://api.twitter.com/oauth2/token"
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.bearer_token = self.get_bearer_token()

    def get_bearer_token(self):
        response = requests.post(
        self.bearer_token_url, 
        auth=(self.consumer_key, self.consumer_secret),
        data={'grant_type': 'client_credentials'},
        headers={"User-Agent": "TwitterDevSampledStreamQuickStartPython"})

        if response.status_code != 200:
            raise Exception(f"Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text))

        body = response.json()
        return body['access_token']

    def __call__(self, r):
        r.headers['Authorization'] = f"Bearer %s" % self.bearer_token
        return r

def stream_connect(auth):
    response = requests.get(stream_url, auth=auth, headers={"User-Agent": "TwitterDevSampledStreamQuickStartPython"}, stream=True)
    for response_line in response.iter_lines():
        if response_line:
            jsonTweet = dict(json.loads(response_line))
            userid = jsonTweet["data"]["author_id"]
            #r = requests.get(user_url+userid, auth=auth, headers={"User-Agent": "TwitterDevSampledStreamQuickStartPython"})
            #jsonUser = json.loads(str(r.text))
            redis_tweet = [
                ("created_at",jsonTweet["data"]["created_at"]),
                ("user:id",userid),
                #("user:profile:imageURL",jsonUser["profile_image_url_https"]),
                #("user:screen_name",jsonUser["screen_name"]),
                #("user:location",jsonUser["location"]),
                ("text",jsonTweet["data"]["text"]) ]
            d = dict(redis_tweet)
            pprint(jsonTweet)
            pprint(d)
            # Add Tweet to Redis Stream
            try :
                redis_client.xadd('twitter', d, maxlen=100000)
            except redis.exceptions.ConnectionError:
                print("Can't connect to Redis DB at: " + host + ":" + str(port))
                # os._exit(1)
            except :
                print("XADD failed, Tweet = " + str(d))
                # os._exit(2)

bearer_token = BearerTokenAuth(consumer_key, consumer_secret)

# Listen to the stream. This reconnection logic will attempt to reconnect as soon as a disconnection is detected.
keepRunning = True
print("CONNECTING")
while keepRunning :
    try :
        stream_connect(bearer_token)
    except (KeyboardInterrupt, SystemExit):
        keepRunning = False
    except : 
        print("Unexpected error")
    print("RECONNECTING")
print( "DONE")
os._exit(0)
