"""

extract textual data from the PM (PubMed) json files. There is one function for PubMed files and one for PubMed central
files, since both are structured slightly differently. In the end, however, only get_abstracts_cut is used for the dataset
as only a set of abstracts was analysed.

"""

import json
mypath = ''

def _removeNonAscii(s): #removes non-ascii chars from string
    return "".join(i for i in s if ord(i)<128)

def getPMCfiles(filename):

    # this function extracts textual data from PMC json files
    # however, for the eval dataset this wasn't used

    with open(mypath+'/pmc_json/'+filename) as json_file:

        data = json.load(json_file)
        title = data['metadata']['title']

        text = []
        for p in data['body_text']:
            text.append(p["text"])

        title = _removeNonAscii(title)
        text[0] = _removeNonAscii(text[0])

        return title, text


def getPMfiles(filename):

    # this function extracts textual data from PMC json files
    # however, for the eval dataset this wasn't used

    with open(mypath+'/pdf_json/' + filename) as json_file:

        data = json.load(json_file)
        title = data['metadata']['title']
        text = []
        for p in data['abstract']:
            text.append(p["text"])

        for p in data['body_text']:
            text.append(p["text"])

        title = _removeNonAscii(title)
        text = ' '.join(text)
        text = _removeNonAscii(text)

        return title, text


def get_full_abstracts(filename):

    #reads in text in the format of full PM abstract summary via pubmed.com

    import re
    with open(filename, 'r') as f:
        text = f.read()

        read = False
        relevant = []
        for i in range(text.__len__()):
            if read == True:
                if text[i] == 'F' and text[i + 1] == 'A' and text[i + 2] == 'U' and text[i + 3] == ' ' and text[
                    i + 4] == '-':
                    read = False
                else:
                    relevant.append(_removeNonAscii(text[i])) #remove non-ascii chars
            else:
                if text[i] == 'A' and text[i + 1] == 'B' and text[i + 2] == ' ' and text[i + 3] == ' ' and text[
                    i + 4] == '-':
                    read = True

        list = ''.join(relevant).replace('B  - ', '').splitlines()
        list2 = []
        for line in list:
            if line.startswith('CI  -'):
                continue
            else:
                list2.append(line)

        #join the list and remove unnecessary headings
        result = ''.join(list2).replace('OBJECTIVE: ', '').replace('BACKGROUND AND IMPORTANCE: ', '').replace('BACKGROUND: ', '').replace('OBJECTIVES: ', '').replace('IMPORTANCE: ', '').replace('INTRODUCTION: ', '').replace('INTRODUCTION AND AIMS: ', '')
        result = re.sub(r'\s[1-9]+\s', ' ', result)
        result = re.sub('(\d+(\.\d+)?%)', '', result)
        result = re.sub('\'', '', result)
        return re.sub(' +', ' ', result) # remove unnecessary spaces


def get_abstracts_cut(filename):

    #reads in text in the format of full PM abstract summary via pubmed.com
    #full abstract set is divided into smaller subsets so they can be analysed by corenlp

    import re
    with open(filename, 'r') as f:
        lines = f.readlines()
        text2 = []
        for line in lines:
            if line.startswith('CI  -'):
                continue
            else:
                text2.append(line)
    #with open(filename, 'r') as f:
        #text = f.read()

    text = ' '.join(text2)
    read = False
    relevant = []
    full = []
    for i in range(text.__len__()):
        if read == True:
            if text[i] == 'F' and text[i + 1] == 'A' and text[i + 2] == 'U' and text[i + 3] == ' ' and text[
                i + 4] == '-':
                read = False
                res = ''.join(relevant).replace('OBJECTIVE: ', '').replace('MATERIALS AND METHODS: ', '').replace(
                    'BACKGROUND AND IMPORTANCE: ', '').replace('BACKGROUND: ', '').replace('OBJECTIVES: ',
                                                                                           '').replace(
                    'IMPORTANCE: ', '').replace('INTRODUCTION: ', '').replace('INTRODUCTION AND AIMS: ', '').replace('B  - ', '')
                res = re.sub('\n', ' ', res)
                res = _removeNonAscii(res)
                res = re.sub(r'\s[1-9]+\s', ' ', res)
                res = re.sub('(\d+(\.\d+)?%)', '', res)
                res = re.sub('\'', '', res)
                full.append(re.sub(' +', ' ', res))
                relevant = []
            else:
                relevant.append(text[i])
        else:
            if text[i] == 'A' and text[i + 1] == 'B' and text[i + 2] == ' ' and text[i + 3] == ' ' and text[
                i + 4] == '-':
                read = True

    splitlist = [i + j + z + y + t + p + w + il + oe + ewr + sfg + brw + eee + www + ettet + opo + werewr + werwer +neun + zwan + ein + zwei + drei + fiere + funfe for i, j, z, y, t,p, w, il , oe , ewr , sfg , brw , eee ,www,ettet,opo, werewr, werwer,neun, zwan ,ein,zwei ,drei, fiere, funfe in zip(full[::5], full[1::6], full[2::7], full[3::8], full[4::9],full[5::10],full[6::11],full[7::12],full[8::13],full[9::14],full[10::15],full[11::16],full[12::17],full[13::17],full[14::18],full[15::19],full[16::20],full[17::21],full[18::22],full[19::23],full[20::25],full[21::26],full[22::27],full[23::28],full[24::29])] #add every 5 articles together

    return splitlist
