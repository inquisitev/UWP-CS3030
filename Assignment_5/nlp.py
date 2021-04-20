import json
from collections import Counter

ranges =[
    (0, 50), (50,100),(100,150)
]

tweets = []
with open('tweets_hydrated.jsonl') as tweetsfile:
    for line in tweetsfile.readlines():
        tweets.append(json.loads(line))

retweets = []
for tweet in tweets:
    retweets.append(tweet['retweet_count'])

# value, occurance
counts = Counter(retweets).most_common()
counts.sort(key = lambda x: x[0])
print([x[1] for x in counts])
