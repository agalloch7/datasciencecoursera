from __future__ import division

from review import Review
from collections import Counter
from operator import itemgetter
from nltk.stem import WordNetLemmatizer
from review import star

from transformers.sentiment import SentimentModel, OpinionModel

class Business(object):
	"""
	Class to store the full corpus of reviews and meta-data 
	about a particular Business. Upon creation, a Business
	generates a list of constituent Review objects. Iterating over a 
	Business iterates over these Review objects. 
	"""

	SENTIMENT_MODEL = SentimentModel()
	OPINION_MODEL = OpinionModel()

	def __init__(self, review_df):
		"""
		INPUT: pandas DataFrame with each row a review, and columns:

			- business_id: id of the business (must be all same)
			- business_name: name of the Business
			- business_overall_stars: average stars rating for this business
			- review_count: number of reviews that exist for this version

			- review_stars: number of stars reviewer gave
			- text: raw text of the review

			- user_name: first name of the user who made review

		Takes raw DataFrame of reviews about a particular Business (where
		each row corresponds to a particular review of the Business, and 
			1. Stores all the metadata associated with the Business
			2. Converts the reviews (rows) into Review objects. 
		"""

		# Store business-level meta data
		self.app_version = str(review_df.version.iloc[0]) #int
		self.business_id = str(review_df.business_id.iloc[0]) # string 
		self.business_name = str(review_df.business_name.iloc[0]) # string

		# Create the list of Reviews for this Business
		self.reviews = [Review(dict(review_row), business=self) for _,review_row in review_df.iterrows()]

	def __iter__(self):
		"""
		INPUT: Business
		OUTPUT: an iterator over the set of reviews for this Business. 
		
		Allows the use of "do_something(review) for review in Business"
		"""
		return self.reviews.__iter__()

	def __str__(self):
		"""
		INPUT: Business
		OUTPUT: string

		Return a string representation of this Business (i.e. the name of the Business)
		"""
		return self.business_name

	## ANALYSIS METHODS ##

	def aspect_based_summary(self):
		"""
		INPUT: Business
		OUTPUT: dict 

		Returns the final output JSON object, encoding the aspect-based
		sentiment summary for the given business, ready to be written to MongoDB, and
		containing everything (in correct orders) that will be displayed by
		the front end. 

		Note: This is the highest level analytical method--effectively "runs" the full
		analysis for this Business. 
		"""

		aspects_raw = self.extract_aspects()

		core_aspects = ['light','Light' ,'Lights' ,'lights', 'lighting','scene', 'Scene','scenes', 'old', 'previous', 'gen', 'Gen' 
		,'room', 'rooms', 'Room', 'home & away', 'Home Away', 'Routine', 'routine', 'groups', 'Siri', 'SiRi', 'HomeKit', 'Home Kit', 
		'Homekit', 'Alexa', 'UX', 'Design', 'designs', 'New', 'Bridge', 'connect', 'uninstall', 'Updates',
		'home away', 'leaving', 'coming','out of home', 'routine', 'grouping', 'group','lab', 'siri', 'homekit', 
		'alexa', 'setting', 'design', 'ux', 'bridge', 'new', 'update']		

		#find duplicate aspect in manual aspect and auto aspect
		aspects = list(set(aspects_raw + core_aspects))

		asp_dict = dict([(aspect, self.aspect_summary(aspect)) for aspect in aspects])

		## merge similar aspects

		words = [w.lower() for w in aspects]
		l = WordNetLemmatizer()
		l_aspects = []
		for w in words:
			l_aspects.append(l.lemmatize(w))

		print l_aspects

		return {'business_id': self.business_id,
				'version': self.app_version,
				'business_name': self.business_name,
				'aspect_summary': asp_dict	
				}

	def aspect_summary(self, aspect):
		"""
		INPUT: business, string (aspect)
		OUTPUT: dict with keys 'pos' and 'neg' which 
		map to a list of positive sentences (strings) and
		a list of negative sentences (strings) correspondingly. 
		
		Gets summary for a *particular* aspect. Summary includes primarily
		the sorted positive/negative sentences mentioning this apsect.
		"""
		one_sents = []
		two_sents = []
		three_sents = []
		four_sents = []
		five_sents = []

		SENTENCE_LEN_MIN_THRESHOLD = 5


		aspect_sents = self.get_sents_by_aspect(aspect)
		print len(aspect_sents)

		for sent in aspect_sents:

			if len(sent.tokenized) < SENTENCE_LEN_MIN_THRESHOLD:
				continue #filter really short sentences

			prob_pos = Business.SENTIMENT_MODEL.get_positive_proba(sent)
			prob_neg = 1 - prob_pos
			prob_opin = Business.OPINION_MODEL.get_opinionated_proba(sent)

			sent_dict = sent.encode()
			# pass a Review instance to get star
			sent_dict['rating'] = star
			sent_dict['prob_pos'] = prob_pos
			sent_dict['prob_neg'] = prob_neg
			sent_dict['prob_opin'] = prob_opin

			if sent_dict['rating'] == 1:
				one_sents.append(sent_dict)
			elif sent_dict['rating'] == 2:
				two_sents.append(sent_dict)
			elif sent_dict['rating'] == 3:
				three_sents.append(sent_dict)
			elif sent_dict['rating'] == 4:
				four_sents.append(sent_dict)
			elif sent_dict['rating'] == 5:
				five_sents.append(sent_dict)

		n_sents = len(one_sents) + len(two_sents) + len(three_sents) + len(four_sents) + len(five_sents) if len(one_sents) + len(two_sents) + len(three_sents) + len(four_sents) + len(five_sents) > 0 else 1

		return {"one": sorted(one_sents, key=itemgetter('prob_neg'), reverse=True), # sort by confidence
				"two": sorted(two_sents, key=itemgetter('prob_neg'), reverse=True), # sort by confidence
				"three": sorted(three_sents, key=itemgetter('prob_neg'), reverse=True), # sort by confidence
				"four": sorted(four_sents, key=itemgetter('prob_pos'), reverse=True), # sort by confidence
				"five": sorted(five_sents, key=itemgetter('prob_pos'), reverse=True), # sort by confidence
				"num_one": len(one_sents),
				"num_two": len(two_sents),
				"num_three": len(three_sents),
				"num_four": len(four_sents),
				"num_five": len(five_sents),
				"frac_pos": len(five_sents) + len(four_sents) / n_sents
				}

	def extract_aspects(self, single_word_thresh=0.002, multi_word_thresh=0.001):
		"""
		INPUT:
			- Business
			- single_word_thresh : how common does a single-word aspect need to be
								   in order to get included in the summary?
			- multi_word_thresh : how common does a multi-word aspect need to be in
								  order to get included in the summary? 

		OUTPUT: list of lists of strings
			- e.g. [['pepperoni','pizza'], ['wine'], ['service']]

		Returns a list of the aspects that are most often commented on in this business. Note
		that, currently, aspect extraction is based on frequent noun-phrase counting. That is, 
		inclusion in the summary is determined by frequency of occurrence across sentences. Note that different
		inclusion thresholds are used for single- and multi-word aspects, as the former tend to be much more 
		noisy (and so higher threshold is needed for high precision).
		"""

		# Get all the candidate aspects in each sentence
		asp_sents = [sent.aspects for rev in self for sent in rev]
		n_sents = float(len(asp_sents))

		single_asps = [] #list of lists (aspects)
		multi_asps = [] #list of lists

		# create single-word and multi-word aspect lists
		for sent in asp_sents: 
			for asp in sent:
				if len(asp) == 1:
					single_asps.append(" ".join(asp))
				elif len(asp) > 1:
					multi_asps.append(" ".join(asp))
				else:
					assert(False), "something wrong with aspect extraction" # shouldn't happen

		# Get sufficiently-common single- and multi-word aspects
		single_asps = [(asp, count) for asp, count in Counter(single_asps).most_common(30) if count/n_sents > single_word_thresh]
		multi_asps = [(asp, count) for asp, count in Counter(multi_asps).most_common(30) if count/n_sents > multi_word_thresh]

		# filter redundant single-word aspects
		single_asps = self.filter_single_asps(single_asps, multi_asps)

		# the full aspect list, sorted by frequency
		all_asps =  [asp for asp,_ in sorted(single_asps + multi_asps, key=itemgetter(1))]
		print all_asps

		return all_asps


	def get_star_by_sent(self, sent):

		return [stars for review in self for sent in review if review.has_sent(sent)]


	def get_sents_by_aspect(self, aspect):
		"""
		INPUT: Business, string (aspect)  
		OUTPUT: List of Sentence objects
		"""
		return [sent for review in self for sent in review if sent.has_aspect(aspect)] 

	def filter_single_asps(self, single_asps, multi_asps):
		"""
		INPUT: list of strings (aspects)
		OUTPUT: list of strings (filtered aspects)

		Filter out those one-word aspects that are subsumed in a multi-word aspect. E.g. 
		filter out "chicken" if "pesto chicken" is a multi-word aspect. 
		"""

		return [(sing_asp, count) for sing_asp, count in single_asps if not any([sing_asp in mult_asp for mult_asp, _ in multi_asps])]




