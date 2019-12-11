# TwitterInsights

Python 3 application that ingests the Twitter sample stream and adds each tweet to a Redis Stream

## Setup

1. Get a Twitter developer account.
2. In Twitter, create an app: For more information, visit https://developer.twitter.com/en/apps.
3. In Twitter, generate Consumer API keys for the app.
4. Redis: Install Redis 5.0. Redis Streams is a new data structure that's available in version 5.0 and above. For more information, visit https://redis.io.
5. In Redis, set your "consumer_key" and "consumer_secret" Twitter credentials
6. Update the app.yaml file with the Redis DB's hostname, port, and password

## [Contributing](CONTRIBUTING.md)

