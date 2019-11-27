from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener

from redis import Redis
import redis

import argparse

# process command line arguments
parser = argparse.ArgumentParser(description="Program to ingest twitter feed into a Redis Stream")
parser.add_argument("-s", "--server", help="Redis endpoint hostname",required=True)
parser.add_argument("-p", "--port", help="Redis endpoint port",required=True)
args = parser.parse_args()

# --host and --port are required
if not args.server or not args.port:
    print("--host and --port are required parameters")
    exit()

# Connect to Redis
redis_client = redis.Redis(
    host=args.server,
    port=args.port,
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
        if isinstance(v, dict) : # and not isinstance(v, (str, bytes, bytearray)):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v,list) :
            items.extend(flatten_list(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v)))
    return dict(items)


pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-78806dd4-42a6-11e4-aed8-02ee2ddab7fe"
pnconfig.ssl = False

pubnub = PubNub(pnconfig)

my_listener = SubscribeListener()
pubnub.add_listener(my_listener)

pubnub.subscribe().channels('pubnub-twitter').execute()
my_listener.wait_for_connect()
print('connected')

while True:
    result = my_listener.wait_for_message_on('pubnub-twitter')
#    print('result.message = ' + str(result.message))
    flattened = flatten_dict(result.message)
#    print('flattened = ' + str(flattened))
    redis_client.xadd('twitter', flattened, maxlen=100000)

pubnub.unsubscribe().channels('pubnub-twitter').execute()
my_listener.wait_for_disconnect()

print('unsubscribed')

