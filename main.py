from jsonfile import get_abstracts_cut
from pipeline import pipeline_integrate, pipeline_extract
from pymetamap.pymetamap import MetaMap
from query import fuse_synonymous_edges, remove_double_rels
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
path = config['DEFAULT']['path']
mm_loc = config['DEFAULT']['mm_loc']

mm = MetaMap.get_instance(mm_loc)


def main():

    abstracts = get_abstracts_cut(path + 'files/pubmed-coronaviru-set-2.txt')
    #abstracts = abstracts[0:10] # one may only use a subset of abstracts for faster testing.

    for file in abstracts:
        triples = pipeline_extract(filename=None, text=file, withcoref=True, mm=mm) #extract relational triplets
        pipeline_integrate(triples) #integrate triplets into the KG

    remove_double_rels('new_KG') #pass over csv file again and remove double edges
    fuse_synonymous_edges('new_KG') #fuse edges with identical node pairs and synonymous meaning


if __name__ == "__main__":

    main()