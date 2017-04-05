import os
import tweepy
from tweepy import OAuthHandler
import nltk
import markovify
import re
import json


# here are our various keys to access twitter, as well as some vars that will be
# used in different functions.

consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
client = tweepy.API(auth)

def tweeter(event, context):  # (event, context) is required for lambda?.
    with open('djt_tweets.json', 'r') as tt:
        good_text = POSifiedText.from_json(json.load(tt))
        api.update_status(good_text.make_short_sentence(140))

def clean_tweet(tweet):
    """
    The formatting regex is stolen wholesale from twilio's great blog post:
    https://www.twilio.com/blog/2016/09/fun-with-markov-chains-python-and-twilio-sms.html
    The fish names are all my fault.
    """
    tweet = re.sub("https?\:\/\/", "", tweet)   #links
    tweet = re.sub("t.co\/([a-zA-Z0-9]+)", "", tweet)
    tweet = re.sub("bit.ly\/([a-zA-Z1-9]+)", "", tweet)
    tweet = re.sub("Video\:", "", tweet)        #Videos
    tweet = re.sub("\n", " ", tweet)             #new lines
    tweet = re.sub("\s+", " ", tweet)           #extra whitespace
    tweet = re.sub("&amp;", "and", tweet)       #encoded ampersands
    # now the silliness begins.
    tweet = re.sub("[H*h*]illary", "Halibut", tweet)
    tweet = re.sub("[F*f*]lynn", "Fish", tweet)
    tweet = re.sub("[S*s*]calia", "Scallop", tweet)
    tweet = re.sub("[P*p*]ence", "Perch", tweet)
    tweet = re.sub("[S*s*]anders", "Sardine", tweet)
    tweet = re.sub("[O*o*]bama", "Otter", tweet)
    tweet = re.sub("[M*m*]elania", "Mackeral", tweet)
    tweet = re.sub("[M*m*]attis", "Mahi-mahi", tweet)
    tweet = re.sub("[T*t*]illerson", "Tilapia", tweet)
    tweet = re.sub("[P*p*]odesta", "Pufferfish", tweet)
    tweet = re.sub("[P*p*]utin", "Piranha", tweet)
    tweet = re.sub("[K*k*]elly", "Keelfish", tweet)
    tweet = re.sub("[S*s*]ean", "Suckerfish", tweet)
    tweet = re.sub("[O*o*](')?[R*r*]eilly", "ORoughy", tweet)
    tweet = re.sub("[O*o*]bama\s?[C*c*]are", "OtterCare", tweet)
    tweet = re.sub("[S*s*]essions", "Shrimpfish", tweet)
    tweet = re.sub("[K*k*]aine", "Kelp", tweet)
    tweet = re.sub("[W*w*]arren", "Walleye", tweet)
    tweet = re.sub("[I*i*]slam(ic)?", "Orca", tweet)
    tweet = re.sub("ISIS", "OSIS", tweet)
    tweet = re.sub("[M*m*]uslim", "Orca", tweet)
    tweet = re.sub("Ted ", "Tetra ", tweet)
    tweet = re.sub("@realdonaldtrump", "@sealdonaldtrump", tweet)

    return tweet


def get_and_process_tweets(user="realdonaldtrump"):
    """
    A function that uses tweepy to download all the tweets by a given `user`,
    processes the tweets for stopwords & weird internet formatting,
    tokenizes the tweets using the NLTK, and then uses markovify to output a
    reusable JSON file for use in generating future tweets.
    """

    all_tweets = []  # a list in which to store DJT's tweets.

    #get DJT's tweets.
    for tweet in tweepy.Cursor(api.user_timeline, id=user).items():
        if tweet.source == 'Twitter for Android':  # only get tweets from DJT's
                                                   # insecure Android phone
            fishy_tweet = clean_tweet(tweet.text)  # and add them to the list.
            all_tweets.append(fishy_tweet)

    # write his crappy tweets to a text file.
    with open('djt_tweets.txt', 'w') as f:
        for tweet in all_tweets:
            f.write(tweet + ' ')  # need the space so they don't stick together.

    # open the file to POS tag it and process the results into JSON.
    with open("djt_tweets.txt") as t:
            text = t.read()
    #
    text_model = POSifiedText(input_text=text, state_size=3)
    model_json = text_model.to_json()

    # save the json to disk for future use.
    with open('djt_tweets.json', 'w', encoding='utf-8') as j:
        json.dump(model_json, j, ensure_ascii=False)


class POSifiedText(markovify.Text):

    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = ["::".join(tag) for tag in nltk.pos_tag(words) ]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


if __name__ == '__main__':
    if os.path.isfile('djt_tweets.json'):
        tweeter()
    else:
        get_and_process_tweets()
