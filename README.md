## Set up
Clone this repository to your local machine.

## Prerequisites
Python3 and pip3 installed
This programm requires some external libraries. Install them by running ```pip3 install -r requirements.txt``` in the cloned repository.

## Path setup
Please change the paths in the ```config.ini``` file to:
* path: path to where this project is located on your machine
* corenlp_env: path to where CoreNLP is located on your machine
* mm_loc: path to where MetaMap is located on your machine


## Running MetaMap

To run Metamap, please:

* first download the latest release [here](https://metamap.nlm.nih.gov/MainDownload.shtml)

* Install and run the MetaMap servers according to the steps given [here](https://metamap.nlm.nih.gov/Docs/README.html)

* follow the instructions given [here]( https://github.com/AnthonyMRios/pymetamap)

Once skrmedpostctl and wsdserverctl are started you are ready to go.

## Files

The test file including 10.000 PM abstracts (pubmed-coronaviru-set-2.txt) as well as the resulting KG files are located in the files folder.