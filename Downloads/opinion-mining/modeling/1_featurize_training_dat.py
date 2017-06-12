"""
1_featurize_training_data.py

This file:
- reads in the hand-tagged training data
- featurizes the training data using the Sentence class
- merges in relevant features from the raw yelp data
- splits data into development and pure holdout sets and writes these to disk

"""

import os
import pandas as pd

PATH_TO_SENT = "/Users/yixuanli/Downloads/opinion-mining/modeling/data/training.csv" # hand-tagged training data


# LOAD THE TRAINING DATA....
print "Reading in the training data..."
final_df = pd.read_csv(PATH_TO_SENT)
final_df.columns = ['reviewer', 'sentence','rating', 'sentiment', 'opinionated'] #clean up column names for merging

# FEATURIZE

## Import Sentence class from this project
import sys
sys.path.append('/Users/yixuanli/Downloads/opinion-mining')
from classes.sentence import Sentence

print "Featurizing the training data frame (may take a little while)"

sents = [Sentence(sent) for sent in final_df.sentence]

for sent, stars in zip(sents, final_df.rating): 
	sent.stars =  stars # pass the number of stars in

featurized_df = pd.DataFrame([sent.get_features() for sent in sents])

featurized_df['sentiment'] = final_df.sentiment
featurized_df = featurized_df[~featurized_df.sentiment.isnull()]
featurized_df['opinionated'] = final_df.opinionated

print "Done."

# Write to disk in two parts (development and pristine holdout)
import random
random.seed(117) #repeatability

print "Writing out a random sample (20%)"
rows = random.sample(featurized_df.index, int(len(featurized_df)*.2))

df_holdout = featurized_df.ix[rows].copy()
df_devel = featurized_df.drop(rows).copy()

# Write to disk
df_holdout.to_csv("./data/featurized_pristine_holdout.csv", index=False)
df_devel.to_csv("./data/featurized_development.csv", index=False)

print "Done."










