import json
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from nltk import ngrams
import emojis
import re

POPULAR_THRESHOLD = 1000
decoded_tweets = []
tweets = []
with open('C:\\Development\\UWP-CS3030\\Assignment_5\\tweets_hydrated.jsonl') as tweetsfile:
    for line in tweetsfile.readlines():
        decoded_tweets.append(json.loads(line))
        tweets.append(line)


# https://ram-parameswaran22.medium.com/a-relatively-faster-approach-for-reading-json-lines-file-into-pandas-dataframe-90b57353fd38
df_inter = pd.DataFrame(tweets)
df_inter.columns = ['json_element']
df_inter['json_element'].apply(json.loads)
df_final = pd.json_normalize(df_inter['json_element'].apply(json.loads))

#https://pbpython.com/pandas-qcut-cut.html
sns.set_style('whitegrid')

df = df_final

#fig2 = plt.figure()
#fig2.add_subplot(df['retweet_count'].plot(kind='hist'))
#plt.show()
print(df['retweet_count'].describe())

print(len([x for x in decoded_tweets if x['retweet_count'] > 1000]))

prepared_tweets = {}
for tweet in decoded_tweets:
    prepped_tweet ={
        "text": tweet['full_text'],
        "hash_tags": [x['text'] for x in tweet['entities']['hashtags']],
        "word_grams": {n: list(ngrams(tweet['full_text'].split(), n)) for n in range(1,6)}, #https://stackoverflow.com/q/50004602
        "character_grams": {n: list(ngrams(tweet['full_text'], n)) for n in range(2,6)}, #https://stackoverflow.com/q/50004602
        "emojis": list(emojis.get(tweet['full_text']) ) , # https://stackoverflow.com/a/43146653
        "popular": True if tweet['retweet_count'] > POPULAR_THRESHOLD else False, 
        "id" : tweet['id']

    }
    prepared_tweets[tweet['id']] = prepped_tweet
    

with open('C:\\Development\\UWP-CS3030\\Assignment_5\\out.json', 'w+') as csvout:
    csvout.write(json.dumps(prepared_tweets))



