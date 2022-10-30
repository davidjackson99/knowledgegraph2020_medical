"""
This file does simple co-occurence identification.
It is not used in the pipeline.
"""



import itertools
import csv
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
mypath = config['DEFAULT']['path']


def combine_entities(lookuplist): #creates list of lists including every possible entity connection
    entities = []
    for entity in lookuplist:
        string = list(entity.values())[0][3:5]
        string = ':'.join(string)
        #entities.append(list(entity.values())[0][3:5])
        entities.append(string)
    #print(entities)
    comparisons = []
    for a, b in itertools.combinations(entities, 2):
        if a != b:
            comparisons.append([a,b])
    return comparisons

def add_cooc(entities): #adds co-occurrences to list
    exists = False #signifies if co-occurrence already exists in CO-OC.csv
    for entity in entities:
        ent1 = entity[0]
        ent2 = entity[1]
        newFile = []
        cooc = open(mypath + 'files/CO-OC', 'r')
        for line in cooc:
            #print(line)
            data = line.split(',')
            if data[0] == ent1 and data[1] == ent2:
                weight = int(data[2]) + 1
                newline = '%s,%s,%s\n' % (data[0], data[1], str(weight))
                newFile.append(newline)
                exists = True
            else:
                newFile.append(line)
        if exists == False:
            newline = '%s,%s,%s\n' % (ent1, ent2, '1')
            newFile.append(newline)

        cooc.close()

        cooc = open(mypath + 'files/CO-OC', 'w')

        for line in newFile:
            cooc.write(line)
        cooc.close()

def cooccurrence(lookuplist):
    combine = combine_entities(lookuplist)
    add_cooc(combine)