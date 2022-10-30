"""

extracts and filters relational triplets with Stanford's CoreNLP.

"""


import corenlp
from nltk import word_tokenize
import os

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

os.environ["CORENLP_HOME"] = config['DEFAULT']['corenlp_env']


def text_annotate(text):
    with corenlp.CoreNLPClient(annotators="tokenize ssplit".split()) as client:
        ann = client.annotate(text, properties={
        'timeout': '5000000',
        'annotators': 'ssplit, openie',
        'outputFormat': 'json'
        })
        #core_nlp_output = client.annotate(text=text, annotators=['openie'], output_format='json')
        triples = []

        for sentence in ann['sentences']:
            striples = []
            for triple in sentence['openie']:
                striples.append(triple)

            copy = striples.copy()

            for i in range(len(striples)): # filter triples
                for j in range(i + 1, len(striples)):
                    if striples[i]['subjectSpan'][0] <= striples[j]['subjectSpan'][0] and striples[i]['subjectSpan'][
                        1] >= striples[j]['subjectSpan'][1] and striples[i]['relationSpan'][0] <= \
                            striples[j]['relationSpan'][0] and striples[i]['relationSpan'][1] >= \
                            striples[j]['relationSpan'][1] and striples[i]['objectSpan'][0] <= \
                            striples[j]['objectSpan'][0] and striples[i]['objectSpan'][1] >= striples[j]['objectSpan'][
                        1]:
                        if striples[j] in copy:
                            copy.remove(striples[j])
                        continue

                    if striples[i]['subjectSpan'][0] >= striples[j]['subjectSpan'][0] and striples[i]['subjectSpan'][
                        1] <= striples[j]['subjectSpan'][1] and striples[i]['relationSpan'][0] >= striples[j]['relationSpan'][0] and striples[i]['relationSpan'][1] <= striples[j]['relationSpan'][1] and striples[i]['objectSpan'][0] >= striples[j]['objectSpan'][0] and striples[i]['objectSpan'][1] <= striples[j]['objectSpan'][
                        1]:
                        if striples[i] in copy:
                            copy.remove(striples[i])

            for triple in copy:
                triples.append({
                    'subject': triple['subject'],
                    'relation': triple['relation'],
                    'object': triple['object']
                })

        return triples


#text = 'ASD-CoV is a novel formulation of intestinally absorbed oral alpha-cyclodextrin as a unique intermittent fasting mimetic (CoM pat. pend). ASD-CoV reduces the serum phospholipids needed during the life cycle of coronaviruses, incl. SARS-CoV-2, which causes COVID-19'
#text = 'ASD-CoV improves autophagy, a process that is involved in the etiology of many age-related diseases, including neurodegenerative diseases, such as Alzheimers, Parkinsons, Huntingtons, amyotrophic lateral sclerosis (ALS), and multiple sclerosis (MS), see the AGING tab.'
##text = 'Entity1 is a betacoronavirus that causes COVID-19. ACE2 is the main entry point for COVID, since entity has affinity to ACE2 receptors. COVID is more contagious than SARS and Mers. SARS symptoms include feve. Mers-COV belongs to the betacoronavirus family and is closely related to entity, DDP4 is related to DDP8.'#, including neurodegenerative diseases, such as Alzheimers, Parkinsons, Huntingtons, amyotrophic lateral sclerosis (ALS), and multiple sclerosis (MS), see the AGING tab.'
#text = 'We show that a daily intake of tripsin improved SARS immensely. Daily intake of tripsin improved SARS. Daily intake of 20 kg of tripsin improved SARS. 20 kg tripsin per day improved SARS. 20 kg tripsin improved SARS. Tripsin daily improved SARS.'

#text = 'The complete reading frame of CsCDPK1 was amplified by PCR and cloned into the ligation independent cloning (LIC) site of protein expression vector AVA0421.'
#text = 'ASD-CoV can be brought to marked within weeks under an NDIN and is safe enough to be taken before an infection has occured. A potential side effect is a slight reduction of body weight from the excretion of the lipids.'
#triples = text_annotate(text)

def extract_triples(text): #relation extraction pipeline
    extract = text_annotate(text)
    triples = []
    for t in extract:
        triple = [t['subject'], t['relation'], t['object']]
        triples.append(triple)
    return triples


def coreference_resolution(text): # coreference resolution

    with corenlp.CoreNLPClient(annotators="tokenize ssplit".split()) as client:
        ann = client.annotate(text, properties={
        'timeout': '5000000',
        'annotators': 'ssplit, coref',
        'outputFormat': 'json'
        })

    fulltext = []

    for sent in ann['sentences']: # replace found coreferences in text
        sentence = []
        for token in sent['tokens']:
            sentence.append(token['originalText'])
        fulltext.append(sentence)

    for coref in ann['corefs'].values():
        representant = ''
        references = []
        for ent in coref:
            if ent['isRepresentativeMention'] == True:
                representant = ent['text']
            else:
                references.append([ent['sentNum'], ent['startIndex'], ent['endIndex']])

        for replace in references:
            fulltext[replace[0]-1][replace[1]-1:replace[2]-1] = [representant]

    for i in range(len(fulltext)):

        fulltext[i] = ' '.join(fulltext[i])

    return ' '.join(fulltext)
