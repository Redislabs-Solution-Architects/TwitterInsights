# TwitterInsights

Python 3 application that ingests the Twitter sample stream and adds each tweet to a Redis Stream

## Setup

1. Get a Twitter developer account.
2. In Twitter, create an app: For more information, visit https://developer.twitter.com/en/apps.
3. In Twitter, generate Consumer API keys for the app.
4. Install Redis OSS or Redis Enterprise. For more information re Streams, visit https://redis.io.
5. In Redis, SET "consumer_key", and SET "consumer_secret", with your Twitter credentials
6. Update the app.yaml file with the Redis DB's hostname, port, and password

## [Contributing](CONTRIBUTING.md)

