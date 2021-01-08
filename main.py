import pandas as pd
import pandas_datareader.data as web
from sentimentAnalysis import SentimentResult
import datetime
import warnings
warnings.filterwarnings("ignore") # included to dismiss warning issued when saving dataframe to .xls file

# example list of stock tickers on which sentiment analysis will be run
# these are the same tickers used to build the example.xls file
watchlist = ["FB", "AAPL", "TSLA", "AMZN", "GOOG", "FSLY", "DDOG", "QS", "PLTR", "RMO"]


def buildSpreadSheet(): # runs sentiment analysis, pulls daily close and percent change and saves to .xls file
    close = []
    percentChange = []
    posAvg = []
    negAvg = []
    neutralAvg = []
    # if during market hours, pulls percent change and closing price from yesterday
    # if after market close, pulls percent change and closing price from today
    if datetime.datetime.now().hour < 16:
        end = datetime.datetime.today() - datetime.timedelta(days=1)
        start = datetime.datetime.today() - datetime.timedelta(days=2)
    else:
        end = datetime.datetime.today()
        start = end - datetime.timedelta(days=1)

    for ticker in watchlist: # pulls stock price data from yahoo finance and runs sentiment analysis for each ticker
        try:
            data = web.DataReader(ticker, "yahoo", start, end)
        except KeyError:
            print("Key error with {}".format(ticker))
        close.append(round(data["Close"][1], 2))
        percentChange.append(round(100 * (data["Close"][1] - data['Close'][0]) / data["Close"][0], 2))

        # set parameters for sentiment analysis here
        # in this case I use 300 max tweets and 50 tweets per query
        sentiment = SentimentResult(ticker, 300, 50, "{}_tweets.txt".format(ticker))

        sentiment.analyze()
        sentiment.getSummary()
        posAvg.append(sentiment.getPositiveAvg())
        negAvg.append(sentiment.getNegativeAvg())
        neutralAvg.append(sentiment.getNeutralAvg())

    dataframe = pd.DataFrame(close, columns=["Close"]) # builds dataframe and exports to .xls
    dataframe.index = watchlist
    dataframe["Percent Change"] = percentChange
    dataframe["Positive Sentiment Average"] = posAvg
    dataframe["Negative Sentiment Average"] = negAvg
    dataframe["Neutral Sentiment Average"] = neutralAvg
    dataframe.to_excel("example.xls")


def saveTweets(): # runs sentiment analysis and saves tweets to text files for each ticker
    for ticker in watchlist:
        sentiment = SentimentResult(ticker, 5, 1, "{}_tweets.txt".format(ticker))
        sentiment.writeTweetsToFile()
        sentiment.getSummary()


def summarize(): # runs sentiment analysis and prints output
    for ticker in watchlist:
        sentiment = SentimentResult(ticker, 5, 1, "{}_tweets.txt".format(ticker))
        sentiment.analyze()
        sentiment.getSummary()


# summarize()
# saveTweets()
buildSpreadSheet()
