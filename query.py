"""
this file performs some simple queries such as important corelations or avg weight etc.

"""
from nltk.corpus import wordnet
import csv
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
mypath = config['DEFAULT']['path']


lemma = nltk.wordnet.WordNetLemmatizer()
wordnet_lemmatizer = WordNetLemmatizer()
sno = nltk.stem.SnowballStemmer('english')

rels = []
proteins = ['aapp', 'amas', 'celf', 'celc', 'cell', 'crbs', 'eico', 'elii', 'enzy', 'gngm', 'horm', 'nnon', 'rcpt',
            'strd', 'vita']
disease = ['acab', 'cgab', 'comd', 'dsyn', 'imft', 'sosym', 'virs']
chem = ['alga', 'antb', 'bacs', 'bact', 'bdsu', 'carb', 'chem', 'chvs', 'clnd', 'fish', 'fngs', 'food', 'hops', 'inch',
        'lipd', 'mobd', 'nsba', 'orch', 'phsu', 'plnt', 'sbst']
drugs = ['bacs','bdsu','clnd','phsu', 'sbst']
corona = 'C23.550.288,C02.782'


def find_important_corels(conceptID):

    #find most important corelations for a certain concept given by its conceptID

    all = []
    with open('/files/KG_main', 'r') as f:

        reader = csv.reader(f)
        for line in reader:
            all.append(line)
    covid_proteins = []
    for line in all:
        if line[1] == conceptID and any(ext in line[9] for ext in proteins):
            covid_proteins.append(line[3:7])
        if line[2] == conceptID and any(ext in line[8] for ext in proteins):
            covid_proteins.append(line[3:7])
    covid_proteins = sorted(covid_proteins, key=lambda x: int(x[3]))
    covid_proteins.reverse()
    print('Protein relations: ', covid_proteins)
    covid_diseases = []
    for line in all:
        if line[1] == conceptID and any(ext in line[9] for ext in disease):
            covid_diseases.append(line[3:7])
        if line[2] == conceptID and any(ext in line[8] for ext in disease):
            covid_diseases.append(line[3:7])
    covid_diseases = sorted(covid_diseases, key=lambda x: int(x[3]))
    covid_diseases.reverse()
    print('Disease relations: ', covid_diseases)
    covid_drugs = []
    for line in all:
        if line[1] == conceptID and any(ext in line[9] for ext in drugs):
            covid_drugs.append(line[3:7])
        if line[2] == conceptID and any(ext in line[8] for ext in drugs):
            covid_drugs.append(line[3:7])
    covid_drugs = sorted(covid_drugs, key=lambda x: int(x[3]))
    covid_drugs.reverse()
    print('Drug relations: ', covid_drugs)


def get_node_semtypes():

    #counts the amount of occcurrance for each semantic type disease/drug/proten/other at the nodes

    included = []
    diseases = 0
    proteinees = 0
    drugsss = 0
    other = 0
    with open('/files/KG_main', 'r') as f:

        reader = csv.reader(f)
        for line in reader:
            if line[1] not in included:
                if any(ele in line[8] for ele in proteins):
                    proteinees = proteinees +1
                elif any(ele in line[8] for ele in disease):
                    diseases = diseases +1
                elif any(ele in line[8] for ele in drugs):
                    drugsss = drugsss +1
                else:
                    other = other +1
                included.append(line[1])

            if line[2] not in included:
                if any(ele in line[9] for ele in proteins):
                    proteinees = proteinees +1
                elif any(ele in line[9] for ele in disease):
                    diseases = diseases +1
                elif any(ele in line[9] for ele in drugs):
                    drugsss = drugsss +1
                else:
                    other = other +1
                included.append(line[2])

        print('diseases ', diseases, 'proteins', proteinees, 'drugs', drugsss, 'other', other)


def get_avg_weight():

    #returns the average and max weight of the graph

    weight = 0
    edges = 0
    max_weight = []
    with open('/files/KG_main', 'r') as f:

        reader = csv.reader(f)
        for line in reader:
            edges += 1
            weight += int(line[6])
            if int(line[6]) > 20:
                print(line[4],line[3], line[5], line[6])
                max_weight.append([line[4],line[3], line[5], line[6]])
    print('AVERAGE WEIGHT ',weight/edges)
    print('MAX WEIGHT ',sorted(max_weight, key=lambda x: x[3],reverse=True))


def join_sublists(l):

    #just a tool function to join two sublists

    out = []
    while len(l) > 0:
        first, *rest = l
        first = set(first)

        lf = -1
        while len(first) > lf:
            lf = len(first)

            rest2 = []
            for r in rest:
                if len(first.intersection(set(r))) > 0:
                    first |= set(r)
                else:
                    rest2.append(r)
            rest = rest2

        out.append(first)
        l = rest

    for i in range(out.__len__()):
        out[i] = list(out[i])

    return out



def are_synonyms(relation1, relation2):

    #this function identifies if two strings are synonymous


    tokens1 = nltk.word_tokenize(relation1)
    tokens2 = nltk.word_tokenize(relation2)

    tokens1 = [word for word in tokens1 if word not in stopwords.words('english')] #remove stop words
    tokens2 = [word for word in tokens2 if word not in stopwords.words('english')] #remove stop words

    tagged1 = nltk.pos_tag(tokens1)
    tagged2 = nltk.pos_tag(tokens2)
    necessary1 = []
    necessary2 = []

    for i in range(tagged1.__len__()):  # remove prepositions
        if tagged1[i][1] not in ['IN', 'TO']:
            necessary1.append(tagged1[i][0])

    for i in range(tagged2.__len__()):  # remove prepositions
        if tagged2[i][1] not in ['IN', 'TO']:
            necessary2.append(tagged2[i][0])

    if necessary1.__len__() >= necessary2.__len__():
        for i in range(necessary2.__len__()):
            necessary2[i] = wordnet_lemmatizer.lemmatize(necessary2[i], pos="v")
        synonyms = necessary1.copy()
        for word1 in necessary1:
            for syn in wordnet.synsets(word1):
                for l in syn.lemmas():
                    synonyms = synonyms + [l.name()]
        if set(necessary2).intersection(set(synonyms)) == set(necessary2):
            return True

    else:
        for i in range(necessary1.__len__()):
            necessary1[i] = wordnet_lemmatizer.lemmatize(necessary1[i], pos="v")
        synonyms = necessary2.copy()
        for word1 in necessary2:
            for syn in wordnet.synsets(word1):
                for l in syn.lemmas():
                    synonyms = synonyms + [l.name()]

        if set(necessary1).intersection(set(synonyms)) == set(necessary1):
            return True

    return False


def fuse_synonymous_edges(filename):

    #fuse edges that have identical nodes and a synonymous relation type.

    with open(mypath + 'files/'+ filename, 'r') as f:

        reader = csv.reader(f)
        alllines = []
        for line in reader:
            alllines.append(line)


    read = []
    newedges = []
    for line in alllines:
        if [line[1]+line[2]] in read: #if edge already read continue
            continue
        else:
            read.append([line[1] + line[2]])
            partneredges = [line]
            for line2 in alllines:
                if line != line2 and line[1] == line2[1] and line[2] == line2[2]: #append all edges that contain c1 and c2
                    partneredges.append(line2)

            if partneredges.__len__() == 1:
                newedges.append(','.join(line))
                continue

            relationtypes = []
            for edge in partneredges:
                relationtypes.append(edge[3]) #append relation type

            singlerelated = []
            for i in range(relationtypes.__len__()):
                for j in range(relationtypes.__len__()):
                    if i!=j:
                        if are_synonyms(relationtypes[i], relationtypes[j]) == True:
                            singlerelated.append([i,j])
                        else:
                            singlerelated.append([i])
                            singlerelated.append([j])

            relatedlist = join_sublists(singlerelated)
            for list1 in relatedlist:
                weight = 0
                relation = ''
                for element in list1:
                    weight += int(partneredges[element][6])
                    if partneredges[element][3] > relation:
                        relation = partneredges[element][3] #take the longest relation type as its the most specific
                newedges.append(','.join([line[0],line[1],line[2],relation,line[4],line[5],str(weight),line[7],line[8],line[9],line[10],line[11]]))

    print(newedges.__len__())

    with open(mypath+'files/'+filename, 'w') as f:

        f.truncate(0)
        for edge in newedges:
            f.writelines(edge+'\n')


def get_relation_type_occ():
    lines = []
    with open('/files/KG_main', 'r') as f:

        reader = csv.reader(f)
        for line in reader:
            lines.append(line)

    proteins = ['aapp', 'amas', 'celf', 'celc', 'cell', 'crbs', 'eico', 'elii', 'enzy', 'gngm', 'horm', 'nnon', 'rcpt',
                'strd', 'vita']
    disease = ['acab', 'cgab', 'comd', 'dsyn', 'imft', 'sosym', 'virs']
    chem = ['alga', 'antb', 'bacs', 'bact', 'bdsu', 'carb', 'chem', 'chvs', 'clnd', 'fish', 'fngs', 'food', 'hops',
            'inch', 'lipd', 'mobd', 'nsba', 'orch', 'phsu', 'plnt', 'sbst']
    allrels = []
    for line in lines:
        data = line
        semtype1 = data[8]
        semtype2 = data[9]
        type1 = 0
        type2 = 0
        if any(ele in semtype1 for ele in proteins):
            type1 = 1
        elif any(ele in semtype1 for ele in disease):
            type1 = 2
        elif any(ele in semtype1 for ele in chem):
            type1 = 3
        if any(ele in semtype2 for ele in proteins):
            type2 = 1
        elif any(ele in semtype2 for ele in disease):
            type2 = 2
        elif any(ele in semtype2 for ele in chem):
            type2 = 3
        if type1 != 0 and type2 != 0:
            reltypes = list(sorted([type1, type2]))
            strings = [str(integer) for integer in reltypes]
            rrr = ''.join(strings)
            allrels.append(rrr)
    print(allrels.__len__())


    from collections import Counter

    allrels = list(allrels)
    print(Counter(allrels))

#get_relation_type_occ()


def remove_multi_edges():

    #this function takes a multigraph and transforms it to a graph without multiple edges

    all = []
    with open('/Users/dj_jnr_99/PycharmProjects/relationz/files/new_new_KG.csv', 'r') as f:

        reader = csv.reader(f)
        for line in reader:
            all.append(line)

    result = []
    for data1 in all:
        l = data1[1:3]
        if data1[1:3] != sorted(data1[1:3]): #sort lists: this removes bi-directional edges
            data1[1], data1[2] = data1[2], data1[1]
            data1[4], data1[5] = data1[5], data1[4]
            data1[8], data1[9] = data1[9], data1[8]
            data1[10], data1[11] = data1[11], data1[10]
        exists = False
        for r in result:
            res = r.split(',')
            if data1[1] == res[1] and data1[2] == res[2] and data1[4] == res[4] and data1[5] == res[5]:
                exists = True
                break
        if exists == False:
            dups = [data1]
            for data2 in all: #scan through all lines again to find the same co-occurrence
                if data2[1:3] != sorted(data1[1:3]): #sort lists: this removes bi-directional edges
                    data2[1], data2[2] = data2[2], data2[1]
                    data2[4], data2[5] = data2[5], data2[4]
                    data2[8], data2[9] = data2[9], data2[8]
                    data2[10], data2[11] = data2[11], data2[10]
                if data1 != data2 and data1[1] == data2[1] and data1[2] == data2[2]:
                    dups.append(data2)
            if dups.__len__() != 1:
                weight = 0
                for w in dups:
                    weight += int(w[6])
                relations = {} #list that shows relation types and their weights
                for element in dups:
                    relations.update({element[3]: int(element[6])})
                max_relation = max(relations, key=lambda k: relations[k]) # relationtype with highest weight
                result.append(','.join(
                    [data1[0], data1[1], data1[2], max_relation, data1[4], data1[5], str(weight), data1[7], data1[8],
                     data1[9], data1[10], data1[11]]))
            else:
                result.append(','.join(data1))


    with open('/Users/dj_jnr_99/PycharmProjects/relationz/files/KG_non_multi', 'w') as f:
        for res in result:
            f.writelines(res+'\n')


def remove_double_rels(filename):

    alllines = []

    with open(mypath + 'files/' + filename, 'r') as f:

        reader = csv.reader(f)
        for line in reader:
            alllines.append(line)

    added = []
    for line in alllines:
        isin = False
        for i in range(added.__len__()):
            if (line[1] == added[i][1] and line[2] == added[i][2] and line[3] == added[i][3]) or (line[1] == added[i][2] and line[2] == added[i][1] and line[3] == added[i][3]):
                w = int(added[i][6]) + int(line[6])
                added[i] = [added[i][0],added[i][1],added[i][2],added[i][3],added[i][4],added[i][5],str(w),added[i][7],added[i][8],added[i][9],added[i][10],added[i][11]]
                isin = True
                break
        if isin == False:
            added.append(line)

    for i in range(added.__len__()):
        added[i] = ','.join(added[i])

    with open(mypath + 'files/' + filename, 'w') as f:
        f.truncate(0)
        for edge in added:
            f.writelines(edge + '\n')





