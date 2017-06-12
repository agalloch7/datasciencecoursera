import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import json
import time
import pandas as pd
import langid

from pymongo import MongoClient
from classes.business import Business
from langdetect import detect

import glob
import os


def read_data():
	"""
	INPUT: None
	OUTPUT: pandas data frame from file
	"""

	list_of_files = glob.glob('app/uploads/*.csv') # * means all if need specific format then *.csv
	latest_file = max(list_of_files, key=os.path.getctime)

	df = pd.read_csv(latest_file, skiprows = 12, usecols=range(0,12))

	if df.Platform == 'iOS':

		keep = ['Date', 'App ID', 'App Name', 'User', 'Version', 'Rating', 'Review']
		df = df[keep]
		df.columns = ['date', 'business_id', 'business_name', 'user_name', 'version', 'review_stars', 'text']

	else:

		df = df[df.Language == 'English']
		keep = ['Date', 'App Name', 'Publisher ID', 'User', 'Rating', 'Review']
		df = df[keep]
		df.columns = ['date', 'business_name', 'business_id', 'user_name', 'review_stars', 'text']

	for rev in df['text']:
    	try:
        	df['lang'] = detect(rev)
    	except:
        	pass

    df = df[df.lang == 'en']

	return df



def filter_date (start_date, end_date, df):

	df['date'] = pd.to_datetime(df['date'])  
	mask = (df['date'] > start_date) & (df['date'] <= end_date)
	df = df.loc[mask]

	return df

def get_reviews_for_version (version, df):
	"""
	INPUT: business id, pandas DataFrame
	OUTPUT: Series with only texts
	
	For a given business id, return the review_id and 
	text of all reviews for that business. 
	"""
	return df[df.version==version]

def filter_language (df):
	df['lang'] = ''
	df['prob'] = ''

	for index, row in df.iterrows():
		df['lang'][index], df['prob'][index] = langid.classify(row['text'])

	return df[df.lang == 'en']

def main(): 

	client = MongoClient()
	db = client.scoretestJune10
	summaries_coll = db.summaries	

	print "Loading data..."
	df = read_data()

	if 'version' in df.columns:
		version = raw_input("Please input version number such as 2.8.0:")
		print "Working on version %s" % version
		df_filtered = get_reviews_for_version(version,df)
		biz = Business(df_filtered)
	else:
		start_date = raw_input("Please input start date for the app reivews:")
		end_date = raw_input("Please input start date for the app reivews:")
		df_filtered = filter_date(start_date, end_date, df)
		biz = Business(filter_language(df_filtered))

	start = time.time()

	summary = biz.aspect_based_summary()
		
	summaries_coll.insert(summary)

	print "Inserted summary for %s into Mongo" % biz.business_name

	elapsed = time.time() - start
	print "Time elapsed: %d" % elapsed


if __name__ == "__main__":
	main()



