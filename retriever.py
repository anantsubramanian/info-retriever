# Program to build an in-memory positional postings list for a collection of documents
# and allow queries to search through the documents using TF x IDF as a weight
# measure for ranking.

from os import listdir
from os.path import isfile, join
from nltk import stem
from nltk.corpus import stopwords
from re import split as splitre
import operator
import pickle

# Get parameters from config file
properties = {}
if isfile("config.cfg"):
	conf = open("config.cfg", "r")
	for line in conf:
		prop = splitre(' |=|#|\r\n|\n', line)
		if prop.__len__() == 0 or prop[0].__len__() == 0:
			continue	
		properties[prop[0]] = prop[1]
	conf.close()

# Number of documents to display in the query
numdocs = 25
if 'numdocs' in properties:
	numdocs = int(properties['numdocs'])

# List of file found in the mentioned (only .txt and .html files included)
docspath = 'Documents'
if 'documentsfolder' in properties:
	docspath = properties['documentsfolder']

files = [ f for f in listdir(docspath) if isfile(join(docspath, f)) and (f.endswith(".txt") or f.endswith(".html")) ]

# Get common English stop words
stop = stopwords.words('english')

# Dictionary mapping document ids to names
documentid = {}
curid = 0

# Dictionary of words, where each word maps to a dictionary of documents
# Each entry of wordindex[someword][somedocument] is a list of positions
# of occurances of word 'someword' in document 'somedocument'
wordindex = {}

# Dictionary of the frequency of terms in documents
tfidfs = {}

# Dictionary that stores the maximum frequency of any word in each document
maxwordf = {}

splitreg = ' |,|\.|\r\n|;|:|\(|\)|\?|"|<|>|#|@|!|$|%|^|&|\*|-|_|=|\+|/|\\|\{|\}|~'

if 'databasechanged' in properties:
	dbchanged = properties['databasechanged']
else:
	print "Has the database changed?: ",
	dbchanged = raw_input().strip()

shouldbuild = True

if(dbchanged.lower().startswith("no")):
	# If the database hasn't changed, retrieve dictionaries from persistent files
	shouldbuild = False
	print "Loading database into memory."
	print "10%..."
	dbfile = open('docid.dat', 'rb')
	documentid = pickle.load(dbfile)
	dbfile.close()
	print "25%..."
	dbfile = open('wordindx.dat', 'rb')
	wordindex = pickle.load(dbfile)
	dbfile.close()
	print "75%..."
	dbfile = open('tfidfs.dat', 'rb')
	tfidfs = pickle.load(dbfile)
	dbfile.close()
	print "90%..."
	dbfile = open('maxwordf.dat', 'rb')
	maxwordf = pickle.load(dbfile)
	dbfile.close()
	print "100%..."
	print "Done!"

if shouldbuild:
	for f in files:
		curfile = open(join("Documents", f), "r")
		documentid[curid] = f
		wordpos = 0
		for line in curfile:
			for word in splitre(splitreg, line):
				if word.__len__() > 0 and not (word.lower() in stop):
					word = word.lower()
					if not (word in wordindex):
						wordindex[word] = {}	# If word hasn't been seen yet, initialize dictionary entry.
					if not (curid in wordindex[word]):
						wordindex[word][curid] = []	# If word not seen in this document yet, add entry.
					if not (word in tfidfs):
						tfidfs[word] = {}
					if not (curid in tfidfs[word]):
						tfidfs[word][curid] = 0
					if not (curid in maxwordf):
						maxwordf[curid] = 1
					tfidfs[word][curid] += 1
					if tfidfs[word][curid] > maxwordf[curid]:
						maxwordf[curid] = tfidfs[word][curid]	# Update max frequency of max word for this document.
					wordindex[word][curid].append(wordpos)
					wordpos += 1
		curid += 1
		print str(curid) + ". Done " + f
		curfile.close()
else:
	curid = documentid.__len__()

print "Index built."

if shouldbuild:
	if 'shouldpersist' in properties:
		shouldpersist = properties['shouldpersist']
	else:
		print "Do you want the index built to be persistent?: ",
		shouldpersist = raw_input().strip()

	if shouldpersist.lower().startswith("yes"):
		print "Saving to disk. Please wait..."
		print "10%..."
		dbfile = open('docid.dat', 'wb')
		pickle.dump(documentid, dbfile)
		dbfile.close()
		print "20%..."
		dbfile = open('wordindx.dat', 'wb')
		pickle.dump(wordindex, dbfile)
		dbfile.close()
		print "75%..."
		dbfile = open('tfidfs.dat', 'wb')
		pickle.dump(tfidfs, dbfile)
		dbfile.close()
		print "90%..."
		dbfile = open('maxwordf.dat', 'wb')
		pickle.dump(maxwordf, dbfile)
		dbfile.close()
		print "100%..."
		print "Done!"

while True:
	print "Please enter your query (or Exit to quit): ",
	query = raw_input().strip()
	if (query.lower().startswith("exit")):
		break
	querylist = [ word.lower() for word in splitre(splitreg, query) if word.__len__() > 0 and not (word.lower() in stop) ]
	doclist = []
	if querylist.__len__() == 0:
		print "Query too general / too vague."
	else:
		for i in range(curid):
			weight = 0
			for word in querylist:
				if word in tfidfs and i in tfidfs[word]:
					weight += tfidfs[word][i]*(float(1) / tfidfs[word].__len__())
			# Total weight for document = (sum of weights for query terms for document) / (max frequency of any word in document)
			doclist.append((documentid[i], weight))
			doclist.sort(key=operator.itemgetter(1), reverse=True)
			num = 1
		for i in doclist:
		 	if num > numdocs:
		 		break
			print str(num) + ". " + i[0] + " TFxIDF = " + str(i[1])
			num += 1
