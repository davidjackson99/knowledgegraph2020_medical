"""

Named Entity recognition with the help of MetaMap.
The following python wrapper for MetaMap is used: https://github.com/AnthonyMRios/pymetamap.git

"""




from tools.sem_types import sem_types
import itertools
import re
#from pymetamap.pymetamap import MetaMap



TAGGER_SERVER_DEFAULT_TCP_PORT=1795
TAGGER_SERVER_TCP_PORT_0=1795
TAGGER_SERVER_TCP_PORT_1=1795



def str_to_list(string):
    li = list(string[1:-1].split(","))
    return li


def multResolve(concepts): #if a concept occurs multiple times it will be saved as one finding with several indexes. This function unpacks the indexes to make several findings
    newlist = []
    for concept in concepts:

        if concept[1]!= 'MMI': #disregard entries from AA
            continue
        if concept[8].startswith('['):
            allindexes = concept[8].replace('[', '').replace(']', '')
            allindexes = re.split(';|,',allindexes)
            for index in allindexes:
                newcon = [concept[0],concept[1],concept[2],concept[3],concept[4],concept[5],concept[6],concept[7],index,concept[9]]
                newlist.append(newcon)
        elif concept[8].count('/') > 1:
            #print(concept[8])
            allindexes = concept[8].replace('[', '').replace(']', '')
            allindexes = re.split(';|,', allindexes)
            for index in allindexes:
                newcon = [concept[0],concept[1],concept[2],concept[3],concept[4],concept[5],concept[6],concept[7],index,concept[9]]
                newlist.append(newcon)
        else:
            newcon = [concept[0], concept[1], concept[2], concept[3], concept[4], concept[5], concept[6], concept[7],
                      concept[8], concept[9]]
            newlist.append(newcon)
    return newlist



def filterCons(concepts): # MetaMap may return several matches for one concept. This function filters out the most important match for each,
    concepts = multResolve(concepts)
    for i, j in itertools.combinations(concepts, 2):
        if i!=j:
            jpos = j[8]
            ipos = i[8]
            jsl = jpos.split('/')
            isl = ipos.split('/')
            if int(isl[0]) == int(jsl[0]): #if both concept start at same index

                if isl[1] > jsl[1]: # match i has wider span than match j
                    try:
                        concepts.remove(j)
                    except:
                        continue
                if isl[1] < jsl[1]: # match j has wider span than match i
                    try:
                        concepts.remove(i)
                    except:
                        continue
                if isl[1] == jsl[1]: #matches have same length
                    jscore = float(j[2])
                    iscore = float(i[2])
                    if jscore > iscore: # take match with higher score
                        try:
                            concepts.remove(i)
                        except:
                            continue
                    if jscore < iscore: # take match with higher score
                        try:
                            concepts.remove(j)
                        except:
                            continue
                    else:
                        try:
                            concepts.remove(j)
                        except:
                            continue

    return concepts

def replaceCons(text, cons): #replace concepts with "placeholders", i.e. decode the text and return lookup list
    n = 0
    res = []
    i = 0
    concepts = sortCons(cons)
    lookuplist =[] #this list contains which entity corresponds to which placeholder
    for concept in concepts:
        #print(concept[3], 'entity'+ str(n))

        startpos = int(concept[8].split('/')[0])-1
        endpos = int(concept[8].split('/')[1]) + startpos
        res.append((text[i:startpos]) + 'xentity'+ str(n))

        lookup = {'xentity'+ str(n): concept}
        lookuplist.append(lookup)
        n = n+1
        i = endpos
    res.append(text[i:])
    return ''.join(res), lookuplist

def sortCons(concepts): #sort concepts by their index
    sorted = []
    for concept in concepts:
        listlen = sorted.__len__()
        for i in range(listlen):
            if int(concept[8].split('/')[0]) < int(sorted[i][8].split('/')[0]):
                sorted.insert(i, concept)
                break
        if listlen == sorted.__len__():
            sorted.append(concept)
    return sorted


def reduceCons(concepts): #only keep concepts that are relevant by semantic type
    relevant = []
    for concept in concepts:
        semtype = str_to_list(concept[5])
        if not set(semtype).isdisjoint(sem_types):  # is semantic type included in semtype list?
            relevant.append(concept)
    return relevant


def removeNoNouns(text, concepts): #Entities should only be nouns, thus we remove all concepts that are other
    import spacy
    nlp = spacy.load("en_ner_bc5cdr_md")
    doc = nlp(text)
    pos = []
    new = []
    for token in doc:
        if token.pos_ != 'PUNCT':
            pos.append(token.pos_)
    for concept in concepts:
        start = int(concept[8].split('/')[0])-1
        end = int(concept[8].split('/')[1]) + start
        con_word_number = text[:start].count(' ')
        word_count = text[:end].count(' ') - con_word_number +1
        if not set(pos[con_word_number:con_word_number+word_count]).isdisjoint(['NOUN', 'PROPN', 'PRON']):
            new.append(concept)

    return new



def removeNoNouns2(concepts): #Entities should only be nouns, thus we remove all concepts that are other
    new = []
    for concept in concepts:
        if 'noun' in concept[6]:
            new.append(concept)
    return new

def NER(t, mm): #takes string and returns the tagged string + a lookup dictionary containing all entities.

    t = re.sub(r'\s[1-9]+\s',' ', t) # single numerical chars mess with the algorithm and are not of interest for the purpose of this model

    text = [t]

    cons, error = mm.extract_concepts(text, [1])

    cons = filterCons(cons)

    cons = reduceCons(cons)

    cons = removeNoNouns2(cons)

    text, lookup = replaceCons(text[0], cons)

    print('tagged text: ',text)

    return text, lookup



def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
             for i in range(wanted_parts) ]

