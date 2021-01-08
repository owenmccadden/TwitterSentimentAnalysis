import tweepy
import sys
import jsonpickle
import urllib
from urllib.request import urlopen
import json
from array import *

consumer_key = "7anmw74p26JCK8J4DEGjQL0zS"
consumer_secret = "FsxM3pcmGVBlNBzEhxoinPzWOSscFND9JLt0mpCVos8KO07Vvs"
access_token = "874027087-Pbdq3O3qapdPZ1VoRDXQ8EfmOgtfTzTaXbPId9Q1"
access_token_secret = "pInQU0iXUsQ87TWrJtyTCVemKjEEYLwFRMzCzHl8bXGB9"

# Creating the authentication object
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

# Creating the API object while passing in auth information
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
if not api:
    print("Can't authenticate")
    sys.exit(-1)

POS = 0
NEG = 1
NEUTRAL = 2


class SentimentResult:

    # count of overall pos, neg, neutral
    overall = array('L')

    def __init__(self, searchQuery, maxTweets, tweetsPerQry, fName):
        self.sinceId = None
        self.fName = fName
        self.max_id = -1
        self.tweetCount = 0

        self.searchQuery = searchQuery
        self.maxTweets = maxTweets
        self.tweetsPerQry = tweetsPerQry

        self.overall.append(0)
        self.overall.append(0)
        self.overall.append(0)
        # averages
        self.neg_total_pct = 0.0
        self.pos_total_pct = 0.0
        self.neutral_total_pct = 0.0

    def getPositive(self):  # returns total number of positive tweets
        return self.overall[POS]

    def getNegative(self):  # returns total number of negative tweets
        return self.overall[NEG]

    def getNeutral(self):  # returns total number of neutral tweets
        return self.overall[NEUTRAL]

    def getPosTotal(self):  # returns total percent of positive tweets
        return self.pos_total_pct

    def getNegTotal(self): # returns total percent of negative tweets
        return self.neg_total_pct;

    def getNeutralTotal(self): # returns total percent of neutral tweets
        return self.neutral_total_pct

    def analyzeTweet(self, tweet_text): # runs sentiment analysis on individual tweet
        url = "http://text-processing.com/api/sentiment/"
        data = urllib.parse.urlencode({'text': tweet_text})
        data = data.encode('ascii')
        content = urlopen(url=url, data=data).read()
        jdata = json.loads(content)
        label = jdata["label"]
        if label == "pos":
            self.overall[POS] = self.overall[POS] + 1
        elif label == "neg":
            self.overall[NEG] = self.overall[NEG] + 1
        elif label == "neutral":
            self.overall[NEUTRAL] = self.overall[NEUTRAL] + 1
        self.neg_total_pct += jdata["probability"]["neg"]
        self.pos_total_pct += jdata["probability"]["pos"]
        self.neutral_total_pct += jdata["probability"]["neutral"]

    def analyze(self): # runs sentiment analysis for specified search query and number of tweets
        while self.tweetCount < self.maxTweets:
            try:
                if self.max_id <= 0:
                    if not self.sinceId:
                        new_tweets = api.search(q=self.searchQuery, count=self.tweetsPerQry)
                    else:
                        new_tweets = api.search(q=self.searchQuery, count=self.tweetsPerQry,
                                                since_id=self.sinceId)
                else:
                    if not self.sinceId:
                        new_tweets = api.search(q=self.searchQuery, count=self.tweetsPerQry,
                                                max_id=str(self.max_id - 1))
                    else:
                        new_tweets = api.search(q=self.searchQuery, count=self.rQry,
                                                max_id=str(self.max_id - 1), since_id=self.sinceId)
                if not new_tweets:
                    print("No more tweets found")
                    break
                for tweet in new_tweets:
                    self.analyzeTweet(jsonpickle.encode(tweet.text, unpicklable=False))
                self.tweetCount += len(new_tweets)
                print("*")
                self.max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                # Just exit if any error
                print("some error : " + str(e))
                break

    def writeTweetsToFile(self): # runs sentiment analysis for search query and writes tweets to text file
        with open(self.fName, 'w') as f:
            while self.tweetCount < self.maxTweets:
                try:
                    if self.max_id <= 0:
                        if not self.sinceId:
                            new_tweets = api.search(q=self.searchQuery, count=self.tweetsPerQry)
                        else:
                            new_tweets = api.search(q=self.searchQuery, count=self.tweetsPerQry,
                                                    since_id=self.sinceId)
                    else:
                        if not self.sinceId:
                            new_tweets = api.search(q=self.searchQuery, count=self.tweetsPerQry,
                                                    max_id=str(self.max_id - 1))
                        else:
                            new_tweets = api.search(q=self.searchQuery, count=self.rQry,
                                                    max_id=str(self.max_id - 1), since_id=self.sinceId)
                    if not new_tweets:
                        print("No more tweets found")
                        break
                    for tweet in new_tweets:
                        f.write(jsonpickle.encode(tweet.text, unpicklable=False) + '\n')
                        self.analyzeTweet(jsonpickle.encode(tweet.text, unpicklable=False))
                    self.tweetCount += len(new_tweets)
                    print("*")
                    self.max_id = new_tweets[-1].id
                except tweepy.TweepError as e:
                    # Just exit if any error
                    print("some error : " + str(e))
                    break

    def getPositiveAvg(self): # returns average positive percent value
        if self.tweetCount == 0:
            print("No tweets for {}".format(self.searchQuery))
        else:
            return round(self.getPosTotal() / self.tweetCount * 100, 2)

    def getNegativeAvg(self): # returns average negative percent value
        if self.tweetCount == 0:
            print("No tweets for {}".format(self.searchQuery))
        else:
            return round(self.getNegTotal() / self.tweetCount * 100, 2)

    def getNeutralAvg(self): # returns average neutral percent value
        if self.tweetCount == 0:
            return
        else:
            return round(self.getNeutralTotal() / self.tweetCount * 100, 2)

    def getSummary(self): # prints summary of sentiment analysis for search query
        print("\nAnalyzed {0} tweets with search query {1}".format(self.tweetCount, self.searchQuery))
        print("Counts: Positive: {0} Negative: {1} Neutral: {2}".format(self.getPositive(),
                                                                        self.getNegative(), self.getNeutral()))
        print("Average probability of a tweet being: Positive {0}% Negative {1}% Neutral {2}%\n".format
              (self.getPositiveAvg(), self.getNegativeAvg(), self.getNeutralAvg()))