import pickle

class SentimentModel(object): 

	SENTIMENT_MODEL = pickle.load(open('/Users/yixuanli/Downloads/opinion-mining/modeling/results/final_models/senti_pred.p', 'rb'))

	def get_positive_proba(self, sent):
		return SentimentModel.SENTIMENT_MODEL.predict_proba(sent.get_features(asarray=True))[0][1]

class OpinionModel(object):

	OPINION_MODEL = pickle.load(open('/Users/yixuanli/Downloads/opinion-mining/modeling/results/final_models/opin_pred.p', 'rb'))

	def get_opinionated_proba(self, sent):
		return OpinionModel.OPINION_MODEL.predict_proba(sent.get_features(asarray=True))[0][1]