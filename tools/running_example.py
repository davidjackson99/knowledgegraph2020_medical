#simple running example

from pipeline import pipeline_extract, pipeline_integrate
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
path = config['DEFAULT']['path']


#type in a text
text = 'SARS, MERS and COVID-19 are coronaviruses. Common symptoms include fever, cough, and pneumonia.'

#or load a paper
filename = path + 'files/pubmed-coronaviru-set-28.txt'

#the withcoref variable can disable coreference resolution in the process, since it take a lot of time. the rest is quite fast
triples = pipeline_extract(filename=filename,text=None,withcoref=False)

print('Found the following triples...')
for triple in triples:
    print(triple)

#you may also load the found triples into a kg csv file. you can do this by uncommenting the following:

"""
KGfile = 'example.csv'

pipeline_integrate(triples, KGfile)

"""