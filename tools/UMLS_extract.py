"""
File for extracting UMLS information from the database files.
It is not used in the pipeline.

"""

pathvariable = ''

def getUMLSTerms(plusID = False):

    #load all terms (+ID) from UMLS database MRCONSO.RRF file

    list = []

    with open(pathvariable + "/MRCONSO.RRF", 'r') as f:

        if(plusID == False):

            for x in f:

                split = x.split('|')

                list.append(split[14])

            s = set(list)
            return (sorted(s))

        else:
            previousterm = ''

            for x in f:

                split = x.split('|')

                if (split[1] == previousterm):

                    previousterm = split[1]

                else:

                    list.append([split[14],split[1]])
                    previousterm = split[1]

            return list

def getRelatedTerms():

    # load all related terms from UMLS database MRREL.RRF file

    terms = []

    with open(pathvariable + "/MRREL.RRF", 'r', encoding='ISO-8859-1') as f:

        for x in f:

            split = x.split('|')
            terms.append([split[0],split[4]])

    return terms

def getUMLSTermIDfromName(Term):

    # returns the ID of a concept name from MRCONSO.RRF

    with open(pathvariable + "MRCONSO.RRF", 'r', encoding='ISO-8859-1') as f:

        for x in f:

            split = x.split('|')

            if (split[14] == Term):

                return split[0]
                break


def getNameFromUMLSID(Term):

    # returns the term name of a concept ID from MRCONSO.RRF

    with open(pathvariable + "/MRCONSO.RRF", 'r', encoding='ISO-8859-1') as f:

        for x in f:

            split = x.split('|')

            if (split[0] == Term):

                return split[14]
                break


def getAllRelatedIDsTo(ID, terms=False):

    # returns all related terms to certain concept (ID) from MRREK.RRF

    with open(pathvariable + "/MRREL.RRF", 'r', encoding='ISO-8859-1') as f:

        related_ids = []
        previous = False

        for x in f:

            split = x.split('|')

            if (split[0] == ID):

                related_ids.append(split[4])
                previous = True

            else:

                if previous == True:
                    break
    if terms == True:

        related_terms = []
        for termid in related_ids:
            name = getNameFromUMLSID(termid)
            related_terms.append(name)

        return [related_ids, related_terms]

    else:

        return related_ids

def verifyRelation(ID1, ID2):

    #take two IDs and check if they are related according to UMLS

    related = getAllRelatedIDsTo(ID1)
    if ID2 in related:
        return True
    else:
        return False