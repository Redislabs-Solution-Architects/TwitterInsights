from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener

from redis import Redis
import redis, socket, os

import argparse

# process command line arguments
parser = argparse.ArgumentParser(description="Program to ingest twitter feed into a Redis Stream")
parser.add_argument("-s", "--server", help="Redis endpoint hostname",required=True)
parser.add_argument("-p", "--port", type=int, help="Redis endpoint port",required=True)
args = parser.parse_args()

# Construct a Redis client
host = args.server
port = args.port
redis_client = redis.Redis(
    host=host,
    port=port,
    decode_responses=True )

def flatten_list(l, parent_key='', sep=':'):
    items = []
    i = 0
    for e in l:
        new_key = parent_key+sep+str(i)
        if isinstance(e, dict) :
            items.extend(flatten_dict(e, new_key, sep=sep).items())
        elif isinstance(e,list) :
            items.extend(flatten_list(e, new_key, sep=sep).items())
        else:
            items.append( (new_key, str(e).strip()) )
        i += 1
    return dict(items)


def flatten_dict(d, parent_key='', sep=':'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k.strip() if parent_key else k.strip()
        if isinstance(v, dict) :
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v,list) :
            items.extend(flatten_list(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v)))
    return dict(items)

# Construct PubNub client
pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-78806dd4-42a6-11e4-aed8-02ee2ddab7fe"
pnconfig.ssl = False
pubnub = PubNub(pnconfig)

# Subscribe to Twitter channel
my_listener = SubscribeListener()
pubnub.add_listener(my_listener)
pubnub.subscribe().channels('pubnub-twitter').execute()
my_listener.wait_for_connect()

# Process published Twitter messages
while True:
    # Get next published Tweet
    result = my_listener.wait_for_message_on('pubnub-twitter')

    # Flatten Tweet's nested content
    flattened = flatten_dict(result.message)
    
    # Add flattened Tweet to a Redis Stream
    try :
        redis_client.xadd('twitter', flattened, maxlen=100000)
    except redis.exceptions.ConnectionError:
        print("Can't connect to Redis DB at: " + host + ":" + str(port))
        os._exit(1)
    except :
        print("XADD failed")
        os._exit(2)

pubnub.unsubscribe().channels('pubnub-twitter').execute()
my_listener.wait_for_disconnect()

os._exit(0)

