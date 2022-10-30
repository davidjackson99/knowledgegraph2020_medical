"""

visualizes and analyses resulting graph

"""
import networkx as nx
import matplotlib.pyplot as plt
import csv
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

mypath = config['DEFAULT']['path'] + 'files/'


def show_degree_histogram(G):
    import matplotlib.pyplot as plt
    import networkx as nx
    m = 3
    degree_freq = nx.degree_histogram(G)
    degrees = range(len(degree_freq))
    plt.figure(figsize=(12, 12))
    plt.loglog(degrees[m:], degree_freq[m:],'go-')
    plt.xlabel('Degree')
    plt.ylabel('Frequency')
    plt.show()


def print_info(G):
    import networkx as nx
    print('DEGREE COEFFICIENT: ',nx.degree_pearson_correlation_coefficient(G))
    print('CLIQUES: ',nx.algorithms.clique.node_clique_number(G))
    print('NUMBER OF CLIQUES: ',nx.algorithms.clique.graph_number_of_cliques(G))
    #print(nx.density(G))
    print(nx.nx.k_nearest_neighbors(G, weight='weight'))
    print(nx.average_degree_connectivity(G))
    #print(nx.average_node_connectivity(G))


def show_full_KG():

    # visualize entire dataset with the Fruchterman-Reingold algorithm. Shown as fig. 4.6 in my thesis

    edges = []
    with open(mypath + 'new_KG', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            concept1 = line[4] + '(' + line[1] + ')'
            concept2 = line[5] + '(' + line[2] + ')'
            edges.append([concept1, concept2, line[3], int(line[6])])
            # print([concept1, concept2, line[3], line[6]])

    G = nx.MultiGraph()

    edgelabels = {}
    for edge in edges:
        G.add_edge(edge[0], edge[1], weight=edge[3], )
        label = {(edge[0], edge[1]): edge[2]}  # set edge label i.e. relation type
        edgelabels.update(label)
        # attrs = {0: {'attr1': 20, 'attr2': 'nothing'}, 1: {'attr2': 3}}
        # nx.set_node_attributes(G, attrs)

    Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
    giant = G.subgraph(Gcc[0])
    #G = giant

    spring_pos = nx.spring_layout(G, k=0.16, weight=0.01)
    #spring_pos = nx.kamada_kawai_layout(G)




    degrees = list(G.degree)
    degrees = [x[1] for x in degrees]
    #colors = [int(x)*10 for x in degrees]
    colors = []

    for degree in degrees:
        if int(degree) > 8 and int(degree) < 20:
            colors.append('dodgerblue')
        elif int(degree) >= 20 and int(degree) < 80:
            colors.append('blue')
        elif int(degree) >= 80 and int(degree) < 250:
            colors.append('darkorchid')
        elif int(degree) >= 250:
            colors.append('crimson')
        else:
            colors.append('deepskyblue')

    degrees = [int(x)-0.7 for x in degrees]
    plt.axis("off")
    nx.draw_networkx(G, pos=spring_pos, node_color=colors, node_size=degrees,
                     with_labels=False, weight=[0.3]*degrees.__len__(), edge_width=[0.3]*degrees.__len__(), width=[0.3]*degrees.__len__())

    #print(nx.info(G))
    degree_cent = nx.degree_centrality(G)
    degree_cent = {k: v for k, v in sorted(degree_cent.items(), key=lambda item: item[1])}

    #print(degree_cent)
    #print(nx.algorithms.clique.node_clique_number(G))
    #print(nx.algorithms.clique.graph_number_of_cliques(G))
    #print(nx.average_clustering(G)) G is multigraph so doesnt work
    #print(nx.average_node_connectivity(G))
    # print(nx.average_shortest_path_length(G)) G is not connected so does not work
    #print(nx.average_degree_connectivity(G))
    #print(nx.nx.k_nearest_neighbors(G, weight='weight'))

    #print(sorted(G.degree, key=lambda x: x[1], reverse=True))

    plt.show()


def drug_star():

    # draws all drugs related to covid with edge weight > 2

    CORONAVIRIDAE = ['C1175743','C0206419','C1175175', 'C3947283', 'C3694279', 'COVID-19', 'C0206750', 'C0026882']
    worsen = ['wors', 'risk', 'boosted', 'threat', 'caus', 'increase likelihood']
    inhibitory = ['inhibit', 'block', 'control', 'inactivates', 'regulate']
    investigation = ['approv', 'investigat', 'may', 'potential']
    treat = ['treat', 'prevent', 'good', 'reduc', 'effectiv', 'protect', 'useful', 'used for']

    drugs=[]
    values=[]
    cc = []
    weights = []
    with open(mypath+'KG_non_multi', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[1] in CORONAVIRIDAE or line[2] in CORONAVIRIDAE:
                #if line[1] in ['C0032310','C1175175','C3947283','C3694279'] or line[2] in ['C0032310','C1175175','C3947283','C3694279'] or line[1] == 'C0206750' or line[2] == 'C0206750' or line[1] == 'C0026882' or line[2] == 'C0026882' or line[1] == 'C0206419' or line[2] == 'C0206419' or line[1] == 'C1175743' or line[1] == 'C1175743' or line[1] == 'COVID-19' or line[2] == 'COVID-19':
                if 'clnd' in line[8] or 'phsu' in line[8] and line[1] not in cc:
                    drugs.append([line[4]])
                    cc.append(line[1])
                    weights.append(int(line[6])/3)
                    if any(word in line[3] for word in worsen):
                        values.append('r')
                    elif any(word in line[3] for word in inhibitory):
                        values.append('g')
                    elif any(word in line[3] for word in investigation):
                        values.append('b')
                    elif any(word in line[3] for word in treat):
                        values.append('black')
                    else:
                        values.append('g')
                elif 'clnd' in line[9] or 'phsu' in line[9] and line[2] not in cc:
                    drugs.append([line[5]])
                    weights.append(int(line[6])/3)
                    if any(word in line[3] for word in worsen):
                        values.append('r')
                    elif any(word in line[3] for word in inhibitory):
                        values.append('g')
                    elif any(word in line[3] for word in investigation):
                        values.append('y')
                    elif any(word in line[3] for word in treat):
                        values.append('b')
                    else:
                        values.append('black')
                    print(line[3])
                    cc.append(line[2])

    drugs = list(map(tuple, drugs))
    print(drugs)
    n = len(drugs)
    df = pd.DataFrame({'source': range(1, n+1),
                       'target':[0]*n,
                       'label': drugs,
                       'value': values,
                       'weight': weights
    })

    nodes = pd.DataFrame({'node' : range(1, n+1),
                          'name' : drugs})

    G = nx.nx.from_pandas_edgelist(df, source='source', target='target', create_using=nx.DiGraph())

    nx.set_node_attributes(G, pd.Series(nodes.name, index=nodes.node).to_dict(), 'name')


    labels={}
    labels[0] = 'Corona'
    for i in range(1,drugs.__len__()-1):
        labels[i] = drugs[i][0]

    plt.figure(figsize=(16,16))

    # node colors
    #val_map = df.iloc[:,:2].set_index('source').to_dict()['new_user']
    #val_map[0] = 2
    #values = [val_map.get(node, 0.25) for node in G.nodes()]


    # Nodes layout/ position
    fixed_positions = {0:(0,0)}
    fixed_nodes = fixed_positions.keys()
    pos = nx.spring_layout(G,pos=fixed_positions, fixed = fixed_nodes, k=15)
    # pos = nx.circular_layout(G, scale=2)

    nx.draw_networkx_labels(G,pos,labels,font_size=12)

    node_sizes = [1000] + [200]*n

    nx.draw(G, cmap=plt.get_cmap('jet'), font_size=10,
            alpha=0.4, node_size=node_sizes, arrows=False,
                   pos=pos, edge_color=df['value'], width=df['weight'])

    plt.show()


def disease_star():

    # draws all diseases related to covid with edge weight > 2

    CORONAVIRIDAE = ['C1175743','C0206419','C1175175', 'C3947283', 'C3694279', 'COVID-19', 'C0206750', 'C0026882']
    disease = ['acab', 'cgab', 'comd', 'dsyn', 'imft', 'sosym', 'virs']
    drugs=[]
    values=[]
    cc = []
    weights = []
    with open(mypath+'KG_non_multi', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[1] in CORONAVIRIDAE and int(line[6]) > 2:
                #if line[1] in ['C0032310','C1175175','C3947283','C3694279'] or line[2] in ['C0032310','C1175175','C3947283','C3694279'] or line[1] == 'C0206750' or line[2] == 'C0206750' or line[1] == 'C0026882' or line[2] == 'C0026882' or line[1] == 'C0206419' or line[2] == 'C0206419' or line[1] == 'C1175743' or line[1] == 'C1175743' or line[1] == 'COVID-19' or line[2] == 'COVID-19':
                if any(word in line[9] for word in disease) and line[1] not in cc and line[2] not in CORONAVIRIDAE:
                    drugs.append([line[5]])
                    if int(line[6]) > 10:
                        weights.append(10)
                    else:
                        weights.append(int(line[6])/3)
                    print(line[3])
                    cc.append(line[2])
                    if any(word in line[3].lower() for word in ['wors', 'risk','complic', 'responsible for']):
                        values.append('r')
                    elif any(word in line[3].lower() for word in ['caus']):
                        values.append('b')
                    elif any(word in line[3].lower() for word in ['associat', 'relat']):
                        values.append('green')
                    else:
                        values.append('black')
            if line[2] in CORONAVIRIDAE and int(line[6]) > 2:
                if any(word in line[8] for word in disease) and line[1] not in cc and line[1] not in CORONAVIRIDAE:
                    drugs.append([line[4]])
                    cc.append(line[1])
                    print(line[3])
                    if int(line[6]) > 10:
                        weights.append(10)
                    else:
                        weights.append(int(line[6])/3)
                    if any(word in line[3].lower() for word in ['wors', 'risk','complic', 'responsible for']):
                        values.append('r')
                    elif any(word in line[3].lower() for word in ['caus']):
                        values.append('b')
                    elif any(word in line[3].lower() for word in ['associat', 'relat']):
                        values.append('pink')
                    else:
                        values.append('black')

    drugs = list(map(tuple, drugs))
    print(drugs)
    n = len(drugs)
    df = pd.DataFrame({'source': range(1, n+1),
                       'target':[0]*n,
                       'label': drugs,
                       'weight': weights,
                       'value': values
    })

    nodes = pd.DataFrame({'node' : range(1, n+1),
                          'name' : drugs})

    G = nx.nx.from_pandas_edgelist(df, source='source', target='target', create_using=nx.DiGraph())

    nx.set_node_attributes(G, pd.Series(nodes.name, index=nodes.node).to_dict(), 'name')


    labels={}
    labels[0] = 'Corona'
    for i in range(1,drugs.__len__()-1):
        labels[i] = drugs[i][0]

    plt.figure(figsize=(16,16))

    # node colors
    #val_map = df.iloc[:,:2].set_index('source').to_dict()['new_user']
    #val_map[0] = 2
    #values = [val_map.get(node, 0.25) for node in G.nodes()]


    # Nodes layout/ position
    fixed_positions = {0:(0,0)}
    fixed_nodes = fixed_positions.keys()
    pos = nx.spring_layout(G,pos=fixed_positions, fixed = fixed_nodes, k=15)
    # pos = nx.circular_layout(G, scale=2)

    nx.draw_networkx_labels(G,pos,labels,font_size=9)

    node_sizes = [1000] + [200]*n

    nx.draw(G, cmap=plt.get_cmap('jet'), font_size=10,
            alpha=0.4, node_size=node_sizes, arrows=False,
                   pos=pos, edge_color=df['value'], width=df['weight'])

    plt.show()


def protein_star():

    # draws all diseases related to covid with edge weight > 2

    CORONAVIRIDAE = ['C1175743','C0206419','C1175175', 'C3947283', 'C3694279', 'COVID-19', 'C0206750', 'C0026882']
    disease = ['aapp', 'amas', 'celf', 'celc', 'cell', 'crbs', 'eico', 'elii', 'enzy', 'gngm', 'horm', 'nnon', 'rcpt', 'strd', 'vita']
    drugs=[]
    values=[]
    cc = []
    weights = []
    with open(mypath+'KG_non_multi', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[1] in CORONAVIRIDAE and int(line[6]) > 2:
                #if line[1] in ['C0032310','C1175175','C3947283','C3694279'] or line[2] in ['C0032310','C1175175','C3947283','C3694279'] or line[1] == 'C0206750' or line[2] == 'C0206750' or line[1] == 'C0026882' or line[2] == 'C0026882' or line[1] == 'C0206419' or line[2] == 'C0206419' or line[1] == 'C1175743' or line[1] == 'C1175743' or line[1] == 'COVID-19' or line[2] == 'COVID-19':
                if any(word in line[9] for word in disease) and line[1] not in cc and line[2] not in CORONAVIRIDAE:
                    drugs.append([line[5]])
                    if int(line[6]) > 10:
                        weights.append(10)
                    else:
                        weights.append(int(line[6])/3)
                    print(line[3])
                    cc.append(line[2])
                    if any(word in line[3].lower() for word in ['wors', 'risk','complic', 'responsible for','death', 'mortal']):
                        values.append('r')
                    elif any(word in line[3].lower() for word in ['control', 'block']):
                        values.append('b')
                    elif any(word in line[3].lower() for word in ['treat', 'improve']):
                        values.append('green')
                    else:
                        values.append('black')
            if line[2] in CORONAVIRIDAE and int(line[6]) > 2:
                if any(word in line[8] for word in disease) and line[1] not in cc and line[1] not in CORONAVIRIDAE:
                    drugs.append([line[4]])
                    cc.append(line[1])
                    print(line[3])
                    if int(line[6]) > 10:
                        weights.append(10)
                    else:
                        weights.append(int(line[6])/3)
                    if any(word in line[3].lower() for word in ['wors', 'risk','complic', 'responsible for','death', 'mortal']):
                        values.append('r')
                    elif any(word in line[3].lower() for word in ['control', 'block']):
                        values.append('b')
                    elif any(word in line[3].lower() for word in ['treat', 'improve']):
                        values.append('green')
                    else:
                        values.append('black')

    drugs = list(map(tuple, drugs))
    print(drugs)
    n = len(drugs)
    df = pd.DataFrame({'source': range(1, n+1),
                       'target':[0]*n,
                       'label': drugs,
                       'weight': weights,
                       'value': values
    })

    nodes = pd.DataFrame({'node' : range(1, n+1),
                          'name' : drugs})

    G = nx.nx.from_pandas_edgelist(df, source='source', target='target', create_using=nx.DiGraph())

    nx.set_node_attributes(G, pd.Series(nodes.name, index=nodes.node).to_dict(), 'name')


    labels={}
    labels[0] = 'Corona'
    for i in range(1,drugs.__len__()-1):
        labels[i] = drugs[i][0]

    plt.figure(figsize=(16,16))

    # node colors
    #val_map = df.iloc[:,:2].set_index('source').to_dict()['new_user']
    #val_map[0] = 2
    #values = [val_map.get(node, 0.25) for node in G.nodes()]


    # Nodes layout/ position
    fixed_positions = {0:(0,0)}
    fixed_nodes = fixed_positions.keys()
    pos = nx.spring_layout(G,pos=fixed_positions, fixed = fixed_nodes, k=15)
    # pos = nx.circular_layout(G, scale=2)

    nx.draw_networkx_labels(G,pos,labels,font_size=12)

    node_sizes = [1000] + [200]*n

    nx.draw(G, cmap=plt.get_cmap('jet'), font_size=15,
            alpha=0.4, node_size=node_sizes, arrows=False,
                   pos=pos, edge_color=df['value'], width=df['weight'])

    plt.show()


def drug_star_with_additional():

    # visualizes drugs connected to COVID-19 and its symptoms

    #CORONAVIRIDAE = ['C1175743','C0206419','C1175175', 'C3947283', 'C3694279', 'COVID-19', 'C0206750', 'C0026882']
    CORONAVIRIDAE = ['COVID-19']
    disease = ['aapp', 'amas', 'celf', 'celc', 'cell', 'crbs', 'eico', 'elii', 'enzy', 'gngm', 'horm', 'nnon', 'rcpt',
               'strd', 'vita']
    worsen = ['wors', 'risk', 'boosted', 'threat', 'caus', 'increase likelihood']
    inhibitory = ['inhibit', 'block', 'control', 'inactivates', 'regulate']
    investigation = ['approv', 'investigat', 'may', 'potential']
    treat = ['treat', 'prevent', 'good', 'reduc', 'effectiv', 'protect', 'useful', 'used for']
    Fever = ['C1457887','C0035222', 'C0041912', 'C0035243', 'C0877203', 'C0032285', 'C0543829', 'C0206061', 'C0015967', 'C0011311', 'C1412002', 'C0850149', 'C1145670', 'C0011991', 'C0700148']
    #Fever = ['C0015967', 'C0850149', 'C0032310', 'C0013404', 'C0032285', 'C0027424', 'C0700148', 'C0011991', 'C1145670']

    includsym=[]
    includcorona=[]
    edges = []
    all=[]
    colors=[]
    with open(mypath+'new_KG', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            #if line[1] in Fever and any(word in line[9] for word in disease):
            if line[1] in Fever and ('clnd' in line[9] or 'phsu' in line[9]):
                if line[2] not in includsym:
                    concept1 = 'SYMPTOMS'
                    concept2 = line[5]
                    includsym.append(line[2])
                    edges.append([concept1, concept2, line[3], int(line[6])])
                    if concept2 not in all:
                        colors.append('red')
                    all.append(concept2)
            #elif line[2] in Fever and any(word in line[8] for word in disease):
            elif line[2] in Fever and ('clnd' in line[8] or 'phsu' in line[8]):
                if line[1] not in includsym:
                    includsym.append(line[1])
                    concept1 = line[4]
                    concept2 = 'SYMPTOMS'
                    edges.append([concept1, concept2, line[3], int(line[6])])
                    if concept1 not in all:
                        colors.append('red')
                    all.append(concept1)
            #elif line[1] in CORONAVIRIDAE and any(word in line[9] for word in disease):
            elif line[1] in CORONAVIRIDAE and ('clnd' in line[9] or 'phsu' in line[9]):
                if line[2] not in includcorona:
                    includcorona.append(line[2])
                    concept1 = 'COVID-19'
                    concept2 = line[5]
                    edges.append([concept1, concept2, line[3], int(line[6])])
                    if concept2 not in all:
                        colors.append('blue')
                    all.append(concept2)
            #elif line[2] in CORONAVIRIDAE and any(word in line[8] for word in disease):
            elif line[2] in CORONAVIRIDAE and ('clnd' in line[8] or 'phsu' in line[8]):
                if line[1] not in includcorona:
                    includcorona.append(line[1])
                    concept1 = line[4]
                    concept2 = 'COVID-19'
                    edges.append([concept1, concept2, line[3], int(line[6])])
                    if concept1 not in all:
                        colors.append('blue')
                    all.append(concept1)

    G = nx.MultiGraph()
    edgelabels = {}
    eeee = []
    for edge in edges:
        G.add_edge(edge[0], edge[1], weight=edge[3], )
        label = {(edge[0], edge[1]): edge[2]}  # set edge label i.e. relation type
        edgelabels.update(label)
        # attrs = {0: {'attr1': 20, 'attr2': 'nothing'}, 1: {'attr2': 3}}
        # nx.set_node_attributes(G, attrs)

    weights = nx.get_edge_attributes(G, 'weight').values()

    pos = nx.spring_layout(G)
    # pos = nx.random_layout(G)
    nx.draw(G, pos,
            width=list(weights),
            node_color='royalblue',
            with_labels=True,
            font_size=7,
            edge_color='lightgrey',
            node_size=40,
            node_width=10)

    #nx.draw_networkx_edge_labels(G, pos)  # displays labels, could turn this on

    ax = plt.gca()

    plt.draw()
    plt.axis('off')
    plt.show()


#Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
#giant = G.subgraph(Gcc[0])
#print(nx.density(giant))
#print(nx.diameter(giant))
#print(nx.info(G))
#print(nx.info(giant))
#print(nx.nx.k_nearest_neighbors(G, weight='weight'))
#print(sorted(G.degree, key=lambda x: x[1], reverse=True)[0:10])
#print_info(giant)
#print(print_info(giant))
