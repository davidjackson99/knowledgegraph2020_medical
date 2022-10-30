"""
preprocess textual data. most of this process aims to cut down or simplify the textual data to make it easier to
apply information extraction (IE) later on.

"""


import re
import spacy
from spacy.matcher import Matcher
from operator import itemgetter

nlp1 = spacy.load("en_ner_bc5cdr_md") # load scispacy

#read more about the dataset here: https://github.com/bionlp-hzau/BioNLP-Corpus.git


def filter_spans(spans):
    """Filter a sequence of spans and remove duplicates or overlaps. Useful for
    creating named entities (where one token can only be part of one entity) or
    when merging spans with `Retokenizer.merge`. When spans overlap, the (first)
    longest span is preferred over shorter spans.

    spans (iterable): The spans to filter.
    RETURNS (list): The filtered spans.
    """
    get_sort_key = lambda span: (span.end - span.start, span.start)
    sorted_spans = sorted(spans, key=get_sort_key, reverse=True)
    result = []
    r2 = []
    seen_tokens = set()
    for span in sorted_spans:
        # Check for end - 1 here because boundaries are inclusive
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
            r2.append([span.start, span.end])
        seen_tokens.update(range(span.start, span.end))
    result = sorted(result, key=lambda span: span.start)
    r2 = sorted(r2, key=itemgetter(0))
    return result, r2



def sentence_start(text): #Remove unnecessary sentence starts like 'This shows that'

    this = ['work', 'data', 'figure', 'reports', 'we', 'this', 'it', 'the', 'study', 'fact','studies', 'our', 'new', 'newest', 'recent', 'above', 'in', 'several','despite']
    have = ['has', 'have', 'is', 'been', 'be']
    shows = ['show', 'shows', 'shown', 'indicates', 'indicate', 'indicated', 'find', 'follow', 'found', 'follows', 'conclude', 'concluded', 'proves', 'proven', 'suggest', 'suggests', 'suggested']

    pattern_quant = [{"LOWER": {"IN": this}, 'OP': '+'}, {"LOWER": {"IN": have}, "OP": '?'}, {"LOWER": {"IN": shows}}, {"LOWER": "that"}]

    matcher = Matcher(nlp1.vocab)
    doc = nlp1(text)
    matcher.add("dose", None, pattern_quant)
    matches = matcher(doc)
    spans = []

    for i in range(matches.__len__()):
        span = doc[matches[i][1]:matches[i][2]]
        spans.append(span)

    sents, inds = filter_spans(spans)
    sentlist = []
    for token in doc:
        sentlist.append(token.text)
    output = ''
    x = 0
    for i in range(inds.__len__()):
        output = output + ' '.join(sentlist[x:inds[i][0]])
        x = inds[i][1]
    output = output + ' '.join(sentlist[x:])
    return output


def remove_braces(s): #remove all braces except braces containing entities.

    s = re.sub(r'\((?![\d|\s|\w]*xentity[\d|\s|\w]*).*?\)', '', s, flags= re.IGNORECASE)

    return s


def getEnum(text): #get all word listings, for example "SARS, MERS, and COVID19".

    matcher = Matcher(nlp1.vocab)
    doc = nlp1(text)

    #not done very elegantly, but it works

    pattern_enum = [{'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                    {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                    {"LOWER": {"IN": ['and', 'or']}}, {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}]

    pattern_enum2 = [{'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                    {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                    {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                    {"LOWER": {"IN": ['and', 'or']}}, {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}]

    pattern_enum3 = [{'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {"LOWER": {"IN": ['and', 'or']}}, {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}]

    pattern_enum4 = [{'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {"LOWER": {"IN": ['and', 'or']}}, {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}]

    pattern_enum5 = [{'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {"LOWER": {"IN": ['and', 'or']}}, {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}]

    pattern_enum6 = [{'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}, {"LOWER": ","},
                     {"LOWER": {"IN": ['and', 'or']}}, {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}]

    matcher.add("enum", None, pattern_enum)
    matcher.add("enum", None, pattern_enum2)
    matcher.add("enum", None, pattern_enum3)
    matcher.add("enum", None, pattern_enum4)
    matcher.add("enum", None, pattern_enum5)
    matcher.add("enum", None, pattern_enum6)
    matches = matcher(doc)
    spans = []

    for i in range(matches.__len__()):
        span = doc[matches[i][1]:matches[i][2]]
        spans.append(span)

    sents, inds = filter_spans(spans)
    sentlist = []
    for token in doc:
        sentlist.append(token.text)
    enums = []
    output = ''
    x = 0
    for i in range(inds.__len__()):
        enums.append(sents[i])
        output = output + ' '.join(sentlist[x:inds[i][0]]) + ' ENUMX' + str(i) + ' '
        x = inds[i][1]
    output = output + ' '.join(sentlist[x:])
    return output, enums



def getIncl(text):

    #get 'including' statements, i.e. statements including 'including' or ', such as'

    matcher = Matcher(nlp1.vocab) #make more efficient for all functions
    doc = nlp1(text)

    pattern_such_as = [{'POS': 'NOUN'}, {"LOWER": ",", 'OP': "?"}, {'LOWER': 'such'}, {'LOWER': 'as'}, {'DEP': 'amod', 'OP': "?"}, {'POS': 'NOUN'}]

    pattern_including = [{'POS': 'NOUN'}, {"LOWER": ",", 'OP': "*"}, {"LOWER": {"IN": ['including', 'namely', 'incl.']}, },
                         {'DEP': 'amod', 'OP': "*"}, {'POS': 'NOUN'}]

    matcher.add("such_as", None, pattern_such_as)
    matcher.add("including", None, pattern_including)
    matches = matcher(doc)
    spans = []

    for i in range(matches.__len__()):
        span = doc[matches[i][1]:matches[i][2]]
        spans.append(span)

    sents, inds = filter_spans(spans)
    sentlist = []
    for token in doc:
        sentlist.append(token.text)
    suchasincl = []
    output = ''
    x = 0
    for i in range(inds.__len__()):
        suchasincl.append(sents[i])
        output = output + ' '.join(sentlist[x:inds[i][0]]) + ' Xyzinclude' + str(i) + ' '
        x = inds[i][1]
    output = output + ' '.join(sentlist[x:])

    return output, suchasincl


def cc_VERB_split(text):

    #example: CPKs are among classes of entityx sensors and are cruicial for functions -> CPKs are among classes of entityx sensors. CPKs are cruicial for functions.

    doc = nlp1(text)
    s_d = []
    sentence = []
    for token in doc:
        t = [token.text, token.dep_, token.head.text, token.pos_,
                [child for child in token.children]]

        sentence.append(t[0])
        s_d.append(t)

    nsubj = ''

    for i in range(s_d.__len__()):
        if s_d[i][1] == 'cc':
            for i2 in range(i+1, s_d.__len__()):
                if s_d[i2][1] in ['conj', 'predet'] and s_d[i2][3] in ['VERB', 'AUX']:

                    if s_d[i][0] in ['and', 'or'] and s_d[i-1][0] == ',' and s_d[i-2][3] == 'VERB': #enumeration of adverbs. this is ok.
                        break
                    for i3 in range(i2, -1, -1):
                        if s_d[i3][1] == 'nsubj' and s_d[i3][3] == 'NOUN':
                            nsubj = '. ' + s_d[i3][0]
                            break
                        if s_d[i3][1] == 'nsubj':
                            nsubj = '. ' + s_d[i3][0]
                        if s_d[i3][1] == 'nsubjpass' and s_d[i3][3] == 'NOUN' and nsubj == '':
                            nsubj = '. ' + s_d[i3][0]

                    sentence = sentence[:i] + [nsubj] + sentence[i+1:]
                    break

                if s_d[i2][3] in ['PROPN', 'NOUN', 'PRON'] or s_d[i2][1] in ['nsubj', 'nmod', 'ROOT', 'pobj', 'dobj', 'nsubjpass']:
                    break

    return ' '.join(sentence)



def pron_sentclause_split(text): #see how many ', which', ', that',... cases there are in a sentence. pass these onto function below
    doc = nlp1(text)
    s_d = []
    sentence = []
    for token in doc:
        t = [token.text, token.dep_, token.head.text, token.pos_,
             [child for child in token.children]]

        sentence.append(t[0])
        s_d.append(t)

    count = 0

    for i in range(s_d.__len__()):

        if s_d[i][0] == ',':

            try:
                if s_d[i + 1][1] in ['nsubj', 'nsubjpass'] and s_d[i + 1][3] == 'PRON':  # which, that, who

                    count += 1
            except:
                continue

        elif s_d[i][0] == 'that' and s_d[i][1] in ['nsubj', 'nsubjpass'] and s_d[i][3] == 'PRON':

            count += 1

    for i in range(count):

        text = pron_sentclause_split_single(text)

    return text



def pron_sentclause_split_single(text):  # X, which is y, is z. -> X is y. X is z. X is a y, which is a z. -> X is a y. Y is a z.
    #just for one such instance. this is why this function can be called multiple times for one sentence
    doc = nlp1(text)
    s_d = []
    sentence = []
    for token in doc:
        t = [token.text, token.dep_, token.head.text, token.pos_,
             [child for child in token.children]]

        sentence.append(t[0])
        s_d.append(t)

    referent = ''
    commaindex = -1
    pronindex = -1

    for i in range(s_d.__len__()):

        if s_d[i][0] == ',':

            if s_d[i + 1][1] in ['nsubj', 'nsubjpass'] and s_d[i + 1][3] == 'PRON':  # which, that, who

                pronindex = i

                for i2 in range(i, -1, -1):  # find the referent

                    if s_d[i2][3] in ['NOUN', 'PROPN'] and s_d[i2][1] not in ['attr', 'ROOT']:  # PROPN?

                        referent = s_d[i2][0]
                        break

                for i3 in range(i + 1, s_d.__len__()):

                    if s_d[i3][0] == ',':
                        commaindex = i3
                        break

                if referent == '':  # no referent found

                    return text

                else:

                    if commaindex == -1:  # no comma found after 'which', 'that',...
                        return ' '.join(sentence[:pronindex] + ['.'] + [referent] + sentence[pronindex + 2:s_d.__len__()])

                    else:  # comma found
                        return ' '.join(sentence[:pronindex] + sentence[commaindex + 1:] + [referent] + sentence[pronindex + 2:commaindex] + ['.'])

        if s_d[i][0] == 'that' and s_d[i][1] in ['nsubj', 'nsubjpass'] and s_d[i][3] == 'PRON':

            pronindex = i

            for i2 in range(i, -1, -1):  # find the referent

                if s_d[i2][3] in ['NOUN', 'PROPN'] and s_d[i2][1] not in ['attr', 'ROOT']:  # PROPN?

                    referent = s_d[i2][0]
                    break

            if referent == '':  # no referent found

                return text

            else:

                return ' '.join(sentence[:pronindex] + ['.'] + [referent] + sentence[pronindex + 1:s_d.__len__()])

    return text



def sent_split(text): #split sentence at certain points such as ",however"
    doc = nlp1(text)
    s_d = []
    sentence = []
    for token in doc:
        t = [token.text, token.dep_, token.head.text, token.pos_,
             [child for child in token.children]]

        sentence.append(t[0])
        s_d.append(t)
    n = 0
    for i in range(s_d.__len__()):
        if s_d[i][1] == 'punct' and i < s_d.__len__()-1:

            if s_d[i+1][0] in ['but', 'however', 'nevertheless']: #find more
                if s_d[i+2][0] == ',':
                    sentence = sentence[:i - n] + ['. '] + sentence[i + 3 - n:]
                    n = n + 1
                else:
                    sentence = sentence[:i-n] + ['. '] + sentence[i+2-n:]
                    n = n + 1

    return ' '.join(sentence)



def preprocess(text): # entire preprocessing pipe
    doc = nlp1(text)
    unfiltered_sent = [sent.string.strip() for sent in doc.sents] #all sentences in list format
    sentencelist = []  # only sentences containing at least 2 concepts.

    for sent in unfiltered_sent:
        if sent.count('xentity') > 1:
            sentencelist.append(sent)
    text = ' '.join(sentencelist)
    text = remove_braces(text) # remove braces noise

    text = sentence_start(text) # remove unecessary sentence start

    text, enums = getEnum(text) # get all enumerations and replace with placeholder

    text, incls = getIncl(text)  # get all "including" statements and replace with placeholder

    doc2 = nlp1(text)
    sents1 = [sent.string.strip() for sent in doc2.sents]
    sents2 = []
    for sent in sents1:
        split = sent_split(sent) #split sentences 1
        divide =  split.split(' . ')  #split new sentences to seperate entities
        sents2 = sents2 + divide
    sents1 = []
    for sent in sents2:

        split = pron_sentclause_split(sent) #split sentences 2
        divide = split.split(' . ') #split new sentences to seperate entities
        for i in range(len(divide)):

            if divide[i].endswith('.') != True:

                divide[i] = divide[i] + '.' #in case there's no dot at sentence end
            divide[i] = re.sub(' +', ' ', divide[i]) #remove unnecessary spaces
        sents1 = sents1 + divide
    sents2 = []
    for sent in sents1:
        split = cc_VERB_split(sent)
        divide = split.split(' . ')  # split new sentences to seperate entities
        for i in range(len(divide)):

            if divide[i].endswith('.') != True:

                divide[i] = divide[i] + '.' #in case there's no dot at sentence end

        sents2 = sents2 + divide


    returnsent = ' '.join((sents2))
    return returnsent, enums, incls

#txt = 'A study of age-specific seasonality for Influenza and RSV in Hong Kong similarly concluded that none of the age groups consistently appear as the driving force for seasonal epidemics [25] . School closure has been adopted as an ILI control strategy based on studies that indicate that children are a major driving force for ILI transmission [26] . A statistical model using sentinel surveillance data from France also indicates that in this setting, where ILI predominates in children, 16-17% of cases may be prevented by school closure. The data presented in the current study indicate that school closure may have limited effect in this setting.'


