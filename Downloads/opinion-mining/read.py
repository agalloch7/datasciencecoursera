from langdetect import detect

def read_data(input_file):
	"""
	INPUT: None
	OUTPUT: pandas data frame from file
	"""
	df = pd.read_csv(input_file, skiprows = 12, usecols=range(0,12))

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


if 'version' in df.columns:
	version = raw_input("Please input version number such as 2.8.0:")
else:
	start_date = raw_input("Please input start date for the app reivews:")
	end_date = raw_input("Please input start date for the app reivews:")

