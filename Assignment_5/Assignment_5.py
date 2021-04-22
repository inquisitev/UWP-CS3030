import json, emojis, re, os
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from nltk import ngrams
from sklearn.tree import DecisionTreeClassifier
from statistics import mean
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier

POPULAR_THRESHOLD = 1000
SAMPLE_COUNT = 50
WORD_GRAM_RANGE = (1,6)
CHARACTER_GRAM_RANGE = (2,6)
DELIMINATOR = ','
HYDRATED_TWEETS_FILE = os.path.join(os.getcwd(), "Assignment_5", "tweets_hydrated.jsonl")
FEATURES_DATA_SET = os.path.join(os.getcwd(), "Assignment_5", "features_data_set.json")
DATA_SET = os.path.join(os.getcwd(), "Assignment_5", "data_set.csv")

def extract_tweets(hydrated_file_path):
    tweets = []
    with open(hydrated_file_path) as tweetsfile:
        for line in tweetsfile.readlines():
            tweets.append(json.loads(line))
    return tweets

# This section was used once to identify some statistics about the dataset, namely the statistical distrobution 
# related to the retweet counts
#
#      count      6851.000000
#      mean       3979.552182
#      std       18071.052423
#      min           0.000000
#      25%           3.000000
#      50%          92.000000
#      75%         834.500000
#      max      169954.000000
#      Name: retweet_count, dtype: float64
#
# https://ram-parameswaran22.medium.com/a-relatively-faster-approach-for-reading-json-lines-file-into-pandas-dataframe-90b57353fd38
#   df_inter = pd.DataFrame(tweets)
#   df_inter.columns = ['json_element']                                        <-| # this might not be necessry because the tweets are converted from json
#   df_inter['json_element'].apply(json.loads)                                   | # in extract_tweets
#   df_final = pd.json_normalize(df_inter['json_element'].apply(json.loads))     |
#   print(df_final['retweet_count'].describe())

# Because 75 percent of tweets are retweeted more than 830 times, i decided that 1000 would be 
# a good threshold to assume popularity.
# print(len([x for x in decoded_tweets if x['retweet_coufnt'] > POPULAR_THRESHOLD])) 
# ==> 1572

# Take the raw, hydrated tweets and process them so that each tweet has its text, hashtags, emojis and any grams 
# for future use
def process_tweets(tweets):
    prepared_tweets = {}
    for tweet in tweets: 
        prepped_tweet ={
            "text": tweet['full_text'],
            "hash_tags": [x['text'] for x in tweet['entities']['hashtags']],
            "word_grams": {n: list(ngrams(tweet['full_text'].split(), n)) for n in range(*WORD_GRAM_RANGE)}, #https://stackoverflow.com/q/50004602
            "character_grams": {n: list(ngrams(tweet['full_text'], n)) for n in range(*CHARACTER_GRAM_RANGE)}, #https://stackoverflow.com/q/50004602
            "emojis": list(emojis.get(tweet['full_text']) ), # https://stackoverflow.com/a/43146653
            "popular": True if tweet['retweet_count'] > POPULAR_THRESHOLD else False, 
            "id" : tweet['id']
        }

        prepared_tweets[tweet['id']] = prepped_tweet
    return prepared_tweets

# Build a global list of all word grams, character grams for thier respective ranges, emojis, and hastags.
def extract_features(tweets):
    word_grams = {n: [] for n in range(*WORD_GRAM_RANGE)}
    character_grams = {n: [] for n in range(*CHARACTER_GRAM_RANGE)}
    emoji_list = []
    hashtags = []
    for tweet in tweets: 
        tweet_word_grams = {n: list(ngrams(tweet['full_text'].split(), n)) for n in range(*WORD_GRAM_RANGE)}
        tweet_character_grams = {n: list(ngrams(tweet['full_text'], n)) for n in range(*CHARACTER_GRAM_RANGE)}
        tweet_emojis = list(emojis.get(tweet['full_text']) ) 
        tweet_hashtags = [x['text'] for x in tweet['entities']['hashtags']]
        for n in range(*WORD_GRAM_RANGE):
            for val in tweet_word_grams[n]:
                word_grams[n].append(val)
        for n in range(*CHARACTER_GRAM_RANGE):
            for val in tweet_character_grams[n]:
                character_grams[n].append(val)

        hashtags[0:0] = tweet_hashtags
        emoji_list[0:0] =  tweet_emojis


    return {
        "word_grams": word_grams,
        "character_grams": character_grams, 
        "emoji_list": emoji_list,
        "hashtags": hashtags
    }

#save the most common features to a file
def save_features_to_file(features, output_path):
    wg,cg,el,h = features.values()

    out_as_json = {
        "word_grams": {n: [x[0] for x in Counter(wg[n]).most_common(SAMPLE_COUNT)] for n in range(*WORD_GRAM_RANGE)},
        "character_grams": {n: [x[0] for x in Counter(cg[n]).most_common(SAMPLE_COUNT)] for n in range(*CHARACTER_GRAM_RANGE)},
        "emoji_list": [x[0] for x in Counter(el).most_common(SAMPLE_COUNT)],
        "hashtags": [x[0] for x in Counter(h).most_common(SAMPLE_COUNT)],
    }

    with open(output_path, 'w+') as featureFile:
        featureFile.write(json.dumps(out_as_json))

    return out_as_json

# Check each feature and see what features the tweet satisfies
def evaluate_tweet_features(tweet, features):

    return {
        "tweet": tweet,
        "NWordGramsFound": {n: any(x in features['word_grams'][n] for x in tweet['word_grams'][n]) for n in range(*WORD_GRAM_RANGE)},
        "NCharacterGramsFound": {n: any(x in features['character_grams'][n] for x in tweet['character_grams'][n])for n in range(*CHARACTER_GRAM_RANGE)},
        "EmojisFound": any(x in features['emoji_list'] for x in tweet['emojis']),
        "Hashtags": any(x in features['hashtags'] for x in tweet['hash_tags']), 

    }

#flatten the dict of each tweet and save the relation ships to the features and label to a csv file.
def make_processed_data_set(tweets, features, output_file):
    headders = ["tweet ID", "Popular"] + [f"{n} Word Gram" for n in range(*WORD_GRAM_RANGE)]+[f"{n} Char Gram" for n in range(*CHARACTER_GRAM_RANGE)]
    headders.append("Emojis")
    headders.append("Hashtags")
    with open(output_file, 'w+') as processing_file:
        
        processing_file.write(DELIMINATOR.join(headders) + '\n')
        for _, tweet in tweets.items():
            evaluated = evaluate_tweet_features(tweet, features)
            out = []
            out.append(str(tweet['id']))
            out.append('1' if tweet['popular'] else '0')
            
            for n in range(*WORD_GRAM_RANGE):
                out.append('1' if evaluated['NWordGramsFound'][n] else '0')
            
            
            for n in range(*CHARACTER_GRAM_RANGE):
                out.append('1' if evaluated['NCharacterGramsFound'][n] else '0')

            out.append('1' if evaluated['EmojisFound'] else '0')
            out.append('1' if evaluated['Hashtags'] else '0')
            processing_file.write(DELIMINATOR.join(out) + '\n')

# Check our data set against each classifier and report accuracy statistics
def check_validation(data_set_path):
    feature_names = ['1 Word Gram','2 Word Gram','3 Word Gram','4 Word Gram','5 Word Gram','2 Char Gram','3 Char Gram','4 Char Gram','5 Char Gram','Emojis','Hashtags']
    column_names = ["tweet ID","Popular"] + feature_names
    df = pd.read_csv(data_set_path, header = 1, delimiter=',', names=column_names )

    classifiers = {
        "Decision Tree Classifier": DecisionTreeClassifier(),
        "Random Forest Classifier": RandomForestClassifier(),
        "Ada Boost Classifier": AdaBoostClassifier()
    }

    X = df[feature_names]
    Y = df.Popular

    for label, classifier in classifiers.items():
        scores = cross_val_score(classifier, X, Y, cv=10)
        print('-' * 90)
        print(label)
        print(f"Scores: {'%, '.join([str(score * 100) for score in scores])}")
        print(f"Average Score: {mean(scores) * 100}%")
        print('-' * 90)
        print()


# DO ALL THE THINGS
tweets = extract_tweets(HYDRATED_TWEETS_FILE)
features = extract_features(tweets)
features = save_features_to_file(features, FEATURES_DATA_SET)
processed_tweets = process_tweets(tweets)
make_processed_data_set(processed_tweets, features,DATA_SET)
check_validation(DATA_SET)



