"""
This file fuses all subprocesses together.
It loads a set of PM files, pre-processes them, tags the NE and extracts the relations. More importantly, it decodes the
entity or word list placeholders in the relations and furthermore integrates relations into the database.
The two key functions are pipeline_extract, which does the entire IE and pipeline_integrate, which loads triples in the graph
"""


import enchant
from nltk.tokenize import word_tokenize
from openIE import extract_triples, coreference_resolution
from jsonfile import getPMCfiles, getPMfiles, get_full_abstracts
from preprocess import preprocess
from NER import NER
#from main import mypath
from cooccurrence import cooccurrence
import uuid
import csv
import re
from configparser import ConfigParser



config = ConfigParser()
config.read('config.ini')
mypath = config['DEFAULT']['path']
dictionary = enchant.Dict('en-US')

def depth(l):

    # tool that returns the depth of a sentence l
    if isinstance(l, list):
        return 1 + max(depth(item) for item in l)
    else:
        return 0


def unpackmultiplecons(triplet):

    #triplets that include multiple concepts in subject or object will be converted to several triplets

    subject = triplet[0]
    relation = triplet[1]
    object = triplet[2]

    if subject == [] or object == []:
        return None, False

    if len(subject) == 1 and len(object) == 1:
        return triplet, False

    newsubjects = []
    for concept in subject:
        newsubjects.append(concept)
    newtriplets = []
    for concept in object:
        for newsubject in newsubjects:
            newtriplets.append([newsubject, relation, concept])

    return newtriplets, True

def word_is_abbreviation(word):

    # checks if word is a biomedical abbreviation

    commonabbreviations = ['e.g.', 'f.e.', 'etc.', 'i.e.', 'n.b.', 'approx.', 'ml.', 'dept.', 'est.', 'misc.', 'doc.', 'mg.', 'kg.', 'g.', 'mg/kg', 'ppm', 'ppb', 'mg/t', 'nl', 'nl/l', 'nl/ml', 'nl/l', 'µl']

    #if (word.__len__() < 6 and '-' in word or '.' in word):

        #if (word not in commonabbreviations):

    if (word.__len__() < 8 and (bool(re.match('^(?=.*[0-9]$)(?=.*[a-zA-Z])', word))== True or word.isupper() and dictionary.check(word) == False or (word.islower() and dictionary.check(word) == False))):

        if (word not in commonabbreviations):

            return True

    return False


def findentities(text, lookup):

    #takes subject/object from OpenIE and returns the concept (if existent) and its context (if existent)

    if isinstance(text, list):
        print(text)
        text = ' '.join(text)
    text = text.replace('entityx', ' entityx')
    wordlist = word_tokenize(text)

    for i in range(wordlist.__len__()):

        if 'xentity' in wordlist[i]:

            wordlist[i] = wordlist[i].replace('-', ' ')
            wordlist[i] = wordlist[i].replace('/', ' ')
            wordlist[i] = wordlist[i].replace('.', ' ')

            if wordlist[i].count('xentity')==2:
                wordlist[i] = wordlist[i][:len(wordlist[i])//2] + ' ' + wordlist[i][len(wordlist[i])//2:]



    concepts = []
    text = ' '.join(wordlist)
    wordlist = word_tokenize(text)

    #MetaMap does not recognize covid-19 as concept, so it is added manually
    if 'covid-19' in text.lower() or 'covid19' in text.lower() or '2019 novel coronavirus disease' in text.lower() or '2019 novel coronavirus infection' in text.lower() or '2019-nCoV infection' in text.lower() or 'coronavirus disease 2019' in text.lower():
        concepts.append(['COVID-19', 'COVID-19', '[virs]', 'C000657245']) #MetaMap doesn't recognize COVID-19

    if 'favilavir' in text.lower() in text.lower():
        concepts.append(['Favilavir', 'Favilavir', '[clnd]', ''])

    if 'remdesivir' in text.lower() in text.lower():
        concepts.append(['remdesivir', 'remdesivir', '[clnd]', ''])

    for i in range(len(wordlist)):
        if wordlist[i].startswith('xentity'):

            index = wordlist[i][7:]
            index = re.sub('[^0-9]','', index) #delete non-numeric chars
            try:
                index = int(index)
            except:
                continue
            try:
                concept = lookup[index].get(wordlist[i])
                concept = concept[3:6] + [concept[9]]
                concepts.append(concept)
                wordlist[i] = '' #wordlist is now "context" of entity if the relation subject/object isn't just the entity itself
            except:
                continue

        elif word_is_abbreviation(wordlist[i]) == True: #word is abbreviation

            concepts.append([wordlist[i], wordlist[i], '????', '????'])

        elif concepts != []:

            wordlist[i] = ''

    wordstring = ' '.join(wordlist)

    return wordstring, concepts



def replaceplaceholders(text, lookup):

    #this function removes entities in the relation of a triplet ('entityx' will be replaced)

    wordlist = word_tokenize(text)
    for i in range(len(wordlist)):
        if wordlist[i].startswith('xentity'):

            index = wordlist[i][7:]
            index = re.sub('[^0-9]','', index) #delete non-numeric chars
            try:
                index = int(index)
            except:
                continue
            try:
                concept = lookup[index].get(wordlist[i])
                concept = concept[3]
                wordlist[i] = concept #replace placeholder with actual entity
            except:
                continue

    return ' '.join(wordlist)

def find_enum(text, enums):

    #decode enum statements

    wordlist = word_tokenize(text)
    result = []
    for i in range(len(wordlist)):

        if wordlist[i].startswith('ENUMX'):

            index = int(wordlist[i][5:])
            result.append(str(enums[index]))

        else:

            result.append(wordlist[i])

    return ' '.join(result)


def find_incl(text, incls):

    #decode 'including' statements

    wordlist = word_tokenize(text)
    result = []

    for i in range(len(wordlist)):

        if wordlist[i].startswith('Xyzinclude'):

            index = int(wordlist[i][10:])
            result.append(str(incls[index]))
        else:
            result.append(wordlist[i])

    for i in range(result.__len__()):
        if 'including' in result[i]:
            split = result[i].split('including')
            newresult = []
            result[i] = split[0]
            newresult.append(' '.join(result))
            result[i] = split[1]
            newresult.append(' '.join(result))
            newrelation = [split[0], ' includes ', split[1]] #need to add sent/doc ID here too
            return newresult, newrelation
        if 'such as' in result[i]:
            split = result[i].split('such as')
            newresult = []
            result[i] = split[0]
            newresult.append(' '.join(result))
            result[i] = split[1]
            newresult.append(' '.join(result))
            newrelation = [split[0], ' includes ', split[1]] #need to add sent/doc ID here too
            return newresult, newrelation
        if 'namely' in result[i]:
            split = result[i].split('namely')
            newresult = []
            result[i] = split[0]
            newresult.append(' '.join(result))
            result[i] = split[1]
            newresult.append(' '.join(result))
            newrelation = [split[0], ' includes ', split[1]] #need to add sent/doc ID here too
            return newresult, newrelation

    return ' '.join(result), None


def pipeline_extract(filename=None, text=None,withcoref=False, mm=None):

    #Pipeline for extracting relational triples from a scientific article

    if filename==None and text==None:

        print('must pass in file or text')
        raise

    elif filename!=None and text!=None:

        print('please only pass in either text or file')
        raise

    if filename !=None:

        text = get_full_abstracts(filename)

    text, entitylist = NER(text, mm=mm) # tag text and return lookup list for tagged entities

    if withcoref==True:
        text = coreference_resolution(text) # coreference resolution. this takes a lot of time.

    text, enums, incls = preprocess(text) # preprocess text

    triples = extract_triples(text) # extract relational triples

    update_tripletss = []

    for triple in triples: # decode all including statements
        if 'Xyzinclude' in triple[0] or 'Xyzinclude' in triple[2]:
            subject, newrelation = find_incl(triple[0], incls)

            if newrelation != None:
                update_tripletss.append(newrelation)

            object, newrelation = find_incl(triple[2], incls)
            if newrelation != None:
                update_tripletss.append(newrelation)
            if isinstance(subject, list) == True:
                for s in subject:
                    update_tripletss.append([s, triple[1], object])

            if isinstance(object, list) == True:
                for o in object:
                    update_tripletss.append([subject, triple[1], o])

        else:
            update_tripletss.append(triple)


    update_triplets = []

    for triple in update_tripletss: # decode all enum statements

        if 'ENUMX' in triple[0] or 'ENUMX' in triple[2]:
            subject = find_enum(triple[0], enums)
            object = find_enum(triple[2], enums)
            update_triplets.append([subject, triple[1], object])
        else:
            update_triplets.append(triple)

    triples = []

    for triple in update_triplets: # decode entities, return all triplets containing concepts in subject and object
        subject = findentities(triple[0], entitylist)[1]
        context, object = findentities(triple[2], entitylist)
        relation = triple[1] + ' ' + context # this appends part in object before entity occurs to the relation
        if 'xentity' in relation: #get rid of placeholders in relation part of triple
            relation = replaceplaceholders(relation,entitylist)
        if 'Xyzinclude' in relation:
            relation = find_incl(relation, incls)
        if 'ENUMX' in relation:
            relation = find_enum(relation, enums)
        triples.append([subject, relation, object])


    update_triplets = []

    for triple in triples: #if there are multiple concepts in subject or object, create new triplets

        newtriples, multi = unpackmultiplecons(triple)
        if newtriples == None:
            continue
        if multi == False:
            #if depth(newtriples) == 3: #remove unnecessary brackets
                #newtriples = newtriples[0]
            update_triplets.append(newtriples)
            continue
        for newtriple in newtriples:
            update_triplets.append(newtriple)


    return update_triplets



def pipeline_integrate(individual_relations, KGfile=mypath + '/files/new_KG'):

    #this function integrates found triplets into the KG

    #for each triplet: check if in G, if not add it to G. check if individuals
    #the KG DB has the following entries:
    # RELATION ID, CUI1, CUI2, relation_type

    for i in range(len(individual_relations)): #give all triplets same amount of brackets
        if len(individual_relations[i][0]) == 4:
            individual_relations[i][0] = [individual_relations[i][0]]
            individual_relations[i][2] = [individual_relations[i][2]]

    for relation in individual_relations: #iterate through triplets

        cui1 = relation[0][0][1]
        r_type = relation[1]
        cui2 = relation[2][0][1]

        if cui1 == cui2: # LOOPS, these should not be added to the model
            continue

        edges = open(KGfile, 'r')
        newFile = []
        e_exists = False # bool to signify whether edge e exists in DB or not
        for line in edges:
            data = line.split(',')
            if data[1] == cui1 and data[2] == cui2 and data[3] == r_type:
                e_exists = True
                weight = int(data[6]) + 1
                newline = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (data[0], data[1], data[2], data[3], data[4], data[5], str(weight), 'X', data[8], data[9], data[10], data[11])
                newFile.append(newline)
            else:
                newFile.append(line)

        relation_ID = str(uuid.uuid4()) #create a relation ID

        if e_exists == False: #edge wasn't found in KG yet
            if isinstance(r_type, str) != True:
                print(r_type, relation)
                continue
            r_type = re.sub(',', ' ', r_type)  # remove commas for csv representation
            r_type = re.sub(' +', ' ', r_type) # remove unnecessary spaces
            newline = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (relation_ID, cui1, cui2, r_type, relation[0][0][0].replace(',',''), relation[2][0][0].replace(',',''), '1', 'X', relation[0][0][2].replace(',','/'), relation[2][0][2].replace(',','/'), relation[0][0][3], relation[2][0][3])
            newFile.append(newline)

        edges.close()

        edges = open(KGfile, 'w')

        for line in newFile:
            edges.write(line)

        edges.close()

        #CHECK IF NODES ALREADY EXIST IN DATABASE
        #no seperate table for nodes needed, so this is commented out
        """
        nodes = open(mypath + '/files/KG_NODES', 'r')
        c1_exists = False  # bool to signify whether concept 1 exists in DB or not
        c2_exists = False  # bool to signify whether concept 2 exists in DB or not
        newFile = []
        for line in nodes:
            data = line.split(',')
            print('data: ',data)
            if data[0] == cui1: #CONCEPT EXISTS IN DB
                c1_exists = True

                if e_exists == False:
                    print('eexist: False: ', data)
                    d = data[4]
                    print(d)
                    rellist = [str(relation_ID),'/',d]
                    print(''.join(rellist))
                    #rellist = '%s,%s\n' % (data[4],relation_ID)
                    #rellist.append(relation_ID)  # ADD THIS RELATION TO NODE RELATIONS
                    newline = '%s,%s,%s,%s,%s' % (data[0], data[1], data[2], data[3], ''.join(rellist))
                else:
                    print('eexist: True: ', data)
                    newline = line

                #newline = line
                newFile.append(newline)

            elif data[0] == cui2: #CONCEPT EXISTS IN DB
                c2_exists = True

                if e_exists == False:
                    print('eexist: False: ', data)
                    d = data[4]
                    print(d)
                    rellist = [str(relation_ID),'/',d]
                    #rellist = '%s,%s\n' % (data[4],relation_ID)
                    #rellist.append(relation_ID)  # ADD THIS RELATION TO NODE RELATIONS
                    newline = '%s,%s,%s,%s,%s' % (data[0], data[1], data[2], data[3], ''.join(rellist))
                else:
                    print('eexist: True: ', data)
                    newline = line

                #newline = line
                newFile.append(newline)

            else: #CONCEPT DOES NOT EXIST IN DB
                print('CCCexist: False: ', line)
                newFile.append(line)

        if c1_exists == False:
            print('c not exist: True: ', line)
            newline = '%s,%s,%s,%s,%s\n' % (relation[0][0][1], relation[0][0][0].replace(',',''), relation[0][0][2].replace(',','/'), relation[0][0][3], str(relation_ID))
            newFile.append(newline)

        if c2_exists == False:
            print('c not exist: True: ', line)
            newline = '%s,%s,%s,%s,%s\n' % (relation[2][0][1], relation[2][0][0].replace(',',''), relation[2][0][2].replace(',','/'), relation[2][0][3], str(relation_ID))
            newFile.append(newline)

        nodes.close()

        nodes = open(mypath + '/files/KG_NODES', 'w')

        for line in newFile:
            nodes.write(line) #add all lines

        nodes.close()"""

#x = pipeline_extract()