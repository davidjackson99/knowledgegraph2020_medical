"""
this file isn't needed in the process - it includes some sketches and ideas that I didn't implement in the pipeline

"""



from __future__ import unicode_literals, print_function
import os
import spacy
from jsonfile import getPMCfiles, getPMfiles
from nltk.tokenize import sent_tokenize, word_tokenize


#en_ner_bionlp13cg_md
#en_ner_jnlpba_md
nlp1 = spacy.load("en_ner_jnlpba_md", disable=['parser', 'tagger', 'textcat']) # this still returns too many false positives
nlp2 = spacy.load("en_ner_bc5cdr_md", disable=['parser', 'tagger', 'textcat'])
nlp3 = spacy.load("en_ner_craft_md", disable=['parser', 'tagger', 'textcat'])


def coref(text): #alternative coreference method. a lot faster but not as good

    nlp1 = spacy.load("en_ner_bc5cdr_md")
    doc = nlp1(text)
    sent_dependencies = []
    sentence = []
    for token in doc:
        t = [token.text, token.dep_, token.head.text, token.head.pos_,
                [child for child in token.children]]
        if t[1] != 'punct':
            sentence.append(t[0])
            sent_dependencies.append(t)

    noun = [] #the full noun we are looking to replace
    root = -1
    newsent = sentence
    for token in range(sent_dependencies.__len__()):
        if sent_dependencies[token][0] in ['it'] and sent_dependencies[token][1] in ['nsubj', 'nsubjpass']: #find "THAT"

            for i1 in range(sent_dependencies.__len__()-(sent_dependencies.__len__()-token+1), -1, -1): #go backwards in list from there

                if sent_dependencies[i1][1] in ['nmod', 'nsubj', 'pobj', 'ROOT']: #search for first word that is nmod or nsubj

                    root = i1
                    noun.append(sent_dependencies[i1][0])
                    break

            if root == -1: #no root found
                break

            for i2 in range(root+1, sent_dependencies.__len__()-(sent_dependencies.__len__()-token)): #go from main noun until "THAT"

                if sent_dependencies[i2][1] in ['cc', 'amod', 'nsubj', 'nmod', 'conj',  'nsubjpass', 'pobj', 'ROOT']: #add all words that belong to noun-substring
                    noun.append(sent_dependencies[i2][0])

                else: #for first word that is not part of substring, stop iteration
                    break
            for i2 in range(root-1, -1, -1):  # go back from main noun until beginning of string

                if sent_dependencies[i2][1] in ['cc', 'amod', 'nsubj', 'nmod', 'conj', 'nsubjpass', 'compound',
                                                'pobj']:  # add all words that belong to noun-substring
                    noun = [sent_dependencies[i2][0]] + noun

                else:  # for first word that is not part of substring, stop iteration
                    break

            newsent = newsent[:token] + ['. ' + ' '.join(noun)] + newsent[token + 1:]
            noun = []

    print(' '.join(newsent))



#The chronic infection model of LCMV represents a well-established and pathophysiologically relevant experimental model for the study of host-pathogen interactions and immune responses that induce a vigorous CD8 T-cell-dependent hepatitis
#Chronic infections represent a particular challenge for the host organism, which is exposed to prolonged inflammation that may predispose to various co-morbidities, such as susceptibility to secondary infections and cancer
#We identified 348 differentially expressed genes in hepatocytes that correlated well with changes observed in bulk liver tissue

def tag_sentence(sent, getspan=False):

    sentence = sent_tokenize(sent)
    docs = nlp1.tokenizer.pipe(sentence)
    first_tag = []
    second_tag = []
    third_tag = []
    helplist = []

    for doc in docs:
        #tag sentence with 3 different spacy models and return set of all
        doc1 = nlp1(str(doc))
        doc2 = nlp2(str(doc))
        doc3 = nlp3(str(doc))

        if getspan==False:

            for ent in doc2.ents:
                second_tag.append([ent.text, ent.label_])
                helplist.append([ent.text, ent.start])

            for ent in doc3.ents:
                if [ent.text, ent.start] not in helplist:
                    third_tag.append([ent.text, ent.label_])
                    helplist.append([ent.text, ent.start])

            for ent in doc1.ents:
                if [ent.text, ent.start] not in helplist:
                    first_tag.append([ent.text, ent.label_])
                    helplist.append([ent.text, ent.start])

        else:

            for ent in doc2.ents:
                second_tag.append([ent.text, ent.start, ent.end, ent.label_])
                helplist.append([ent.text, ent.start])

            for ent in doc3.ents:
                if [ent.text, ent.start] not in helplist:
                    third_tag.append([ent.text, ent.start, ent.end, ent.label_])
                    helplist.append([ent.text, ent.start])

            for ent in doc1.ents:
                if [ent.text, ent.start] not in helplist:
                    first_tag.append([ent.text, ent.start, ent.end, ent.label_])
                    helplist.append([ent.text, ent.start])


    all = second_tag + third_tag + first_tag

    return all


def place_sentence_tags(sentence): #places '<' '>' at entities and returns tagged sentence

    tags = tag_sentence(sentence, True)

    for tag1 in tags: #gets rid of ['virus', 6, 7, 'TAXON'], ['corona virus', 5, 7, 'ENTITY'] and just makes it ['corona virus', 5, 7, 'ENTITY']
        start1, end1 = tag1[1], tag1[2]
        for tag2 in tags:
            start2, end2 = tag2[1], tag2[2]
            if tag1 == tag2:
                continue
            else:
                if start1 <= start2 and end1 >= end2:
                    tags.remove(tag2)

    sentlist = word_tokenize(sentence)
    for tag in tags:
        start, end = tag[1], tag[2]
        if start == end:
            sentlist[start] = '<' + sentlist[start] + ' ' + tag[3] +  '>'
        else:
            sentlist[start] = '<' + sentlist[start]
            sentlist[end-1] = sentlist[end-1] + ' ' + tag[3] + '>'

    return ' '.join(sentlist)


def getNaiveCoocurrences(conceptpairs):

    #Scan through large number of .con files and see if certain concept relations co-occur in variety of documents

    allconcepts = []
    conceptpairs = [(conceptpairs[i], conceptpairs[j]) for i in range(len(conceptpairs)) for j in range(i + 1, len(conceptpairs))] #all possible relations
    allconcepts.append(conceptpairs)
    allconcepts = sum(allconcepts, [])

    return allconcepts



def subtree_matcher(doc):
    subjpass = 0

    for i, tok in enumerate(doc):
        # find dependency tag that contains the text "subjpass"
        if tok.dep_.find("subjpass") == True:
            subjpass = 1

    x = ''
    y = ''

    # if subjpass == 1 then sentence is passive
    if subjpass == 1:
        for i, tok in enumerate(doc):
            if tok.dep_.find("subjpass") == True:
                y = tok.text

            if tok.dep_.endswith("obj") == True:
                x = tok.text

    # if subjpass == 0 then sentence is not passive
    else:
        for i, tok in enumerate(doc):
            if tok.dep_.endswith("subj") == True:
                x = tok.text

            if tok.dep_.endswith("obj") == True:
                y = tok.text

    return x, y



def filter_triples(triples): #OLD FUNCTION that filters necessary triples. a more efficient and correct version below.

    subjects = []
    relations = []
    objects = []

    for triple in triples:

        subjects.append(triple['subject'])
        relations.append(triple['relation'])
        objects.append(triple['object'])

    for i in range(len(subjects)):
        for j in range(i + 1, len(subjects)):
            subject1 = word_tokenize(subjects[i])
            subject2 = word_tokenize(subjects[j])
            if all(word in subject1 for word in subject2):  # does obj1 contain all words of obj2
                subjects[j] = subjects[i]
            elif all(word in subject2 for word in subject1):
                subjects[i] = subjects[j]

    for i in range(len(relations)):
        for j in range(i + 1, len(relations)):
            relation1 = word_tokenize(relations[i])
            relation2 = word_tokenize(relations[j])
            if all(word in relation1 for word in relation2):  # does obj1 contain all words of obj2
                relations[j] = relations[i]
            elif all(word in relation2 for word in relation1):
                relations[i] = relations[j]

    for i in range(len(objects)):
        for j in range(len(objects)):
            object1 = word_tokenize(objects[i])
            object2 = word_tokenize(objects[j])
            if all(word in object1 for word in object2):  # does obj1 contain all words of obj2
                objects[j] = objects[i]
            elif all(word in object2 for word in object1):
                objects[i] = objects[j]
    newtriples = []
    for x in range(subjects.__len__()):
        newtriples.append({'subject': subjects[x], 'relation': relations[x], 'object': objects[x]})

    newtriples = [dict(s) for s in set(frozenset(d.items()) for d in newtriples)]
    """for x in range(newtriples.__len__()):
        if newtriples[x]['relation'] in newtriples[x]['object']: #['Reduced Aβ load', 'shifting precursor protein processing toward', 'precursor protein processing'] -> ['Reduced Aβ load', 'shifting toward', 'precursor protein processing']
            #print(newtriples[x]['relation'], newtriples[x]['object'])
            print(newtriples[x]['object'], newtriples[x]['relation'])
            newtriples[x]['object'] = newtriples[x]['object'].replace(newtriples[x]['object'],'')"""
    return newtriples



