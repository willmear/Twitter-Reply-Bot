import tweepy
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time
from textblob import TextBlob

import Credentials


# TWITTER CLIENT
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = tweepy.API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets


# TWITTER AUTHENTICATOR
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(Credentials.CONSUMER_KEY, Credentials.CONSUMER_SECRET)
        auth.set_access_token(Credentials.ACCESS_TOKEN, Credentials.ACCESS_TOKEN_SECRET)
        return auth


# TWITTER STREAMER
class TwitterStreamer():

    # Class for streaming and processing live tweets.

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # handles Twitter authentication and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        # filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)


# TWITTER STREAM LISTENER
class TwitterListener(StreamListener):

    # basic listener that just prints received tweets to stdout.

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # returning false on on_data method in case rate limit occurs (mentioned below)
            return False
        print(status)


if __name__ == '__main__':

    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()

    message = "Insert reply message here."
    bot_id = int(api.me().id_str)
    tweet_id = 1
    while True:
        tweets = [status for status in tweepy.Cursor(api.search, q="Insert search term (to find tweets to reply to).")
            .items(100)]
        for tweet in tweets:
            print("Tweet Found")
            print(f"{tweet.author.screen_name} - {tweet.text}")
            tweet_id = tweet.id
            if tweet.in_reply_to_status_id is None and tweet.author.id != bot_id:
                try:
                    print("Attempting Reply...")
                    api.update_status(message.format(tweet.author.screen_name), in_reply_to_status_id=tweet.id_str,
                                      auto_populate_reply_metadata=True)
                    print("Successful Reply")
                except Exception as exc:
                    print(exc)
            time.sleep(10)  # Will send a new tweet every 10 seconds. This was implemented because twitter limits the
            # amount of tweets you can send every hour or so. So, I didn't want to skip over tweets
            # I could possibly reply to. Instead, we take it slow and reply to every tweet.
            # Realistically, this still needs to be higher.
