import json
import os
from os.path import join, dirname
from watson_developer_cloud import AlchemyLanguageV1

alchemy_language = AlchemyLanguageV1(api_key=os.environ.get('ALCHEMY_API_KEY'))
potential_save_responses = ['positive', 'neutral']
# negative

string = ''
combined_operations = ['doc-sentiment']
resp = alchemy_language.combined(text=string, extract=combined_operations)
sentiment = resp['docSentiment']['type']