## Philips Hue App Review ABSA

ABSA is an automated system that uses machine learning and natural language processing to generate a digestable, human-understandable, and browsable summary of the opinions expressed in a corpus of app reviews about Hue app. The summary aims to provide the user with an at-a-glance understanding of a restaurant's features (or *aspects*) as well as reviewers' attitudes towards these features. 


The system generates a summary of this form in a completely automated fashion from the raw text (and metadata) of App reviews about a restaurant. The items in blue at the top are the "aspects" that the algorithm has extracted from the reviews ("routine", "colors", "Alexa" etc.). These are the salient features of the app that reviewers often comment on. 

When one of the aspects is selected, the system displays a summary of reviewers' attitudes towards the aspect based on rating star.

### Code Overview

The main directories of interest are `./classes`, which contains the code for the system's primary summary-generation pipeline, and `./modeling`, which contains the code for training/optimizing the machine learning models that currently power the system.  

To run the code that generates aspect summary, execute main.py, to start the front-end, execute app.py in the app folder.

### References

The problem of automatic review summarization has been addressed in academic literature. See especially: 

* Blair-Goldensohn et al.'s ["Building a Sentiment Summarizer for Local Service Reviews"](http://www.ryanmcd.com/papers/local_service_summ.pdf) (2008)
* Bing Liu's [Sentiment Analysis and Opinion Mining](http://www.cs.uic.edu/~liub/FBS/SentimentAnalysis-and-OpinionMining.pdf) (2012)
* Hu & Liu's [Mining and Summarizing Customer Reviews](http://users.cis.fiu.edu/~lli003/Sum/KDD/2004/p168-hu.pdf) (2004)
