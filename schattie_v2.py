import string
import re
from nltk.corpus import wordnet as wn 
import nltk 
from nltk.corpus.reader.wordnet import WordNetCorpusReader

INITCAP = re.compile('[A-Z].*') 
SOME_LOWERCASE = re.compile('.*[a-z].*')
STARTS_AT = re.compile('@.*')
STARTS_HASH = re.compile('#.*')
STARTS_HTTP = re.compile('http_COLON.*')

END_SENTENCE = re.compile('^([\.\?!]{1,1})$')
#DIDN'T work good the acronyms 
POSSIBLE_ACRONYM = re.compile('((^[A-Z]{2,3}$)|(^[A-Z]{1}[\.]{1}[A-Z]{1}[\.]{1}$)|(^[A-Z]{1}[\.]{1}[A-Z]{1}[\.]{1}[A-Z]{1}[\.]{1}$))')
#the emoticons didn't work too good either 
POSSIBLE_EMOTICON = re.compile('^(([XxOo]+)|(:\))|(;\))|(:P)|(:D)|(;\-\))|(\*\-\))|(\*\))|(;\-\])|(;\])|(;D)|(;\^\))|(:\-,\)))$')

#IGNORE_TOKEN = re.compile('^([\.\?!~`@#$%\^&*\(\)\+=\-\|\\_\{\}\[\]\<\>]{2,})$')

#WORD_FORM = re.compile(['''a-zA-Z0-9\'''']{1,})

days_of_weeks = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", 
            "saturday"]
months = ["january", "fabruary", "march", "april", "may", "june", "july", "august", 
            "september", "october", "november", "december"]
#with open('data/words.txt') as f:
#    dictionary = f.readlines()

dictionary = set(line.strip() for line in open('data/words.txt'))
#dictionary = set(line.strip() for line in open('data/words2.txt'))

common_names = set(line.strip() for line in open('data/common_names.txt'))

common_surnames = set(line.strip() for line in open('data/common_surnames_conv3.txt')) 


print('loading wordnet')
wn = WordNetCorpusReader(nltk.data.find('corpora/wordnet'), None)
print('done loading')
S = wn.synset
L = wn.lemma

tweetSentences = list([])

class TokenSentenceData:
    def __init__(self, token, tokenId):
        self.token = token    # instance variable unique to each instance
        self.tokenId = tokenId

    def __str__(self): 
        return self.token

class Cluster:
#     = 'canine'         # class variable shared by all instances
    def __init__(self, cluster, word, cant):
        self.cluster = cluster    # instance variable unique to each instance
        self.word = word
        self.cant = int(cant)
    
    def __str__(self):
        return "Word: " + str(self.word) + " cluster: "  + str(self.cluster) + \
            " cant: " + str(self.cant) 


loadedClusters = {}

print "loading clusters"
with open("data/clusters.txt") as input:
#with open("data/clusters3.txt") as input:
    lines = (line.strip().split('\t') for line in input)
    for line in lines: 
        loadedClusters[line[1]] = Cluster(line[0],line[1],line[2])

loadedClustersKeys = set(loadedClusters.keys())

print "end loading clusters"

print "loading national places"
loadedNationalPlaces = set([])
with open("data/2014_Gaz_place_national.txt") as input:
    lines = (line.strip().split('\t') for line in input)
    for line in lines: 
        place = line[3].split(' ')
        extractedPlace = '' 
        for word in place: 
            if(word[0].islower() or word=="CDP"):
                break 
            extractedPlace = extractedPlace + word + ' '
        loadedNationalPlaces.add(extractedPlace.strip().lower())
#loadedClustersKeys = set(loadedClusters.keys())

print "end loading national places"



def read_file(filename):
    r"""Assume the file is the format
    word \t tag
    word \t tag
    [[blank line separates sentences]]
    
    This function reads the file and returns a list of sentences.  each
    sentence is a pair (tokens, tags), each of which is a list of strings of
    the same length.
    """
    sentences = open(filename).read().strip().split("\n\n")
    ret = []
    for sent in sentences:
        lines = sent.split("\n")
        pairs = [L.split("\t") for L in lines]
        tokens = [tok for tok,tag in pairs]
        tags = [tag for tok,tag in pairs]
        ret.append( (tokens,tags) )
    return ret



def clean_str(s):
    """Clean a word string so it doesn't contain special crfsuite characters"""
    return s.replace(":","_COLON_").replace("\\", "_BACKSLASH_")

def clean_str2(s):
    toret = s.replace("&amp;","&")
    if(toret.lower()=="at&t"):
        pass 
    return toret

count = 0 
def extract_features_for_sentence1(tokens):
    global count 
    N = len(tokens)
    feats_per_position = [set() for i in range(N)]
    whole_sentence = ''


    for t in range(N): 
        whole_sentence = whole_sentence + tokens[t] + ' '


    posTag = list([])

        
    chainCapitalized = False
    currentSentence = list([])
    for t in range(N):
        count = count + 1


        w = clean_str(tokens[t])
        #lowercased version of the lexical wordform , decreased! :P 
        #produces lower f-score

        feats_per_position[t].add("word=%s" % w)



        if(t>0):
            #the prevPosTagWord doesnt work! because some sentences are hard to parse
            # because nnp also do not correlate with entities such as Sunday for instance ?
#            feats_per_position[t].add("prevPosTagWord=%s" % posTag[t-1][1])
#            feats_per_position[t].add("prevWord=%s" % tokens[t-1].lower())
            feats_per_position[t].add("prevWordN=%s" % tokens[t-1])
        if(t>1):
#            feats_per_position[t].add("prev2Word=%s_%s" % (tokens[t-2].lower(),tokens[t-1].lower()))
            feats_per_position[t].add("prev2NWord=%s_%s" % (tokens[t-2],tokens[t-1]))
        if(t<N-1):
            feats_per_position[t].add("posteriorWord=%s" % (tokens[t+1]))
        if(t<N-2):
            feats_per_position[t].add("posteriorWord=%s_%s" % (tokens[t+1], tokens[t+2]))


        if(t<N-1):
#            feats_per_position[t].add("postPosTagWord=%s" % posTag[t+1][1])

            feats_per_position[t].add("postWord=%s" % tokens[t+1])
        if(t<N-1 and t>0):
            if(tokens[t]==tokens[t+1] and tokens[t]==tokens[t-1]):
                feats_per_position[t].add("sameTokenAsBeforeAndAfter")
##        clean_str2 produces lower f-score :P 
        cleanedToken = tokens[t] #clean_str2(tokens[t]) #tokens[t] #clean_str2(tokens[t])
        if(cleanedToken.lower() in loadedClustersKeys):            
             feats_per_position[t].add("cluster_" + loadedClusters[cleanedToken.lower()].cluster)
#DIDN'T WORK!!! maybe because the clusters are too generic to be taken into account
#they are not as the words such as "at xxx" where we know that whatever comes after 
#at can be an entity
        if(t>0 and tokens[t-1].lower() in loadedClustersKeys):
            feats_per_position[t].add("clusterprev_" + loadedClusters[tokens[t-1].lower()].cluster)

        if(t<N-1 and tokens[t+1].lower() in loadedClustersKeys):
            feats_per_position[t].add("clusterafter_" + loadedClusters[tokens[t+1].lower()].cluster)


        #feats_per_position[t].add("word=%s" % w.lower())
#        if(not STARTS_AT.match(w.strip())):
#            feats_per_position[t].add("notStartsAt")
#
#        if(not STARTS_HASH.match(w.strip())):
#            feats_per_position[t].add("notStartsHash")

#        if(STARTS_AT.match(w.strip()) or STARTS_HASH.match(w.strip()) or 
#            STARTS_HTTP.match(w.strip())):
#            feats_per_position[t].add("StartsForbidden")

        if(STARTS_AT.match(w.strip())):
            feats_per_position[t].add("startsAt")

        if(STARTS_HASH.match(w.strip())):
            feats_per_position[t].add("startsHash")

        if(STARTS_HTTP.match(w.strip())):
            feats_per_position[t].add("startsHttp")


        for i in range(1, 2):
            text = getString(i, tokens, t)
            if(checkObject(text)==1 and len(text)>1):
                pass #doesn't increase too much
#                markFeats(i,feats_per_position,t,"object")

#        feats_per_position[t].add("lenWord_" + str(len(tokens[t])))
       #
        if(tokens[t].lower() not in dictionary):
            feats_per_position[t].add("notInDictionary")
            if(checkLocation(tokens[t])==1 and len(tokens[t])>1):
                markFeats(i,feats_per_position,t,"locationB")
#                if(checkArtifact(text)==1 and len(text)>1):
#                    markFeats(i,feats_per_position,t,"artifact")
#
            if(checkNationalPlaces(tokens[t]) and len(tokens[t])>1):
                markFeats(i,feats_per_position,t,"nationalPlaceB")


            if(t>0):
                if("possibleName" in feats_per_position[t-1] and 
                    "possibleSurname" in feats_per_position[t-1]):
                    pass

            if(tokens[t].lower() not in list(["ok"]) and 
                tokens[t].lower() not in days_of_weeks and 
                tokens[t].lower() not in months 
                #and len(tokens[t])>2
                ):
                if(tokens[t].upper() in common_surnames):
                    feats_per_position[t].add("possibleName")
                if(
                    tokens[t].upper() in common_names
                            ):
                    feats_per_position[t].add("possibleSurname")

        for i in range(2, 6):
            for offset in range(i):
                if(not (offset>=1 and t+1==(len(tokens))) and (t+1-i+offset)>=0):
                    text = getStringV2(i, tokens, t, offset)

                    if(checkLocation(text)==1 and (i-offset)==1):
                        markFeats(i,feats_per_position,t,"locationB")
                    elif(checkLocation(text)==1 and (not (i-offset)==1)):
                        markFeats(i,feats_per_position,t,"locationI")

                    if(checkNationalPlaces(text)==1 and (i-offset)==1):
                        markFeats(i,feats_per_position,t,"nationalPlaceB")
                    elif(checkNationalPlaces(text)==1 and (not (i-offset)==1)):
                        markFeats(i,feats_per_position,t,"nationalPlaceI")


        cntUpper = sum(1 for c in whole_sentence if c.isupper())

        if(not tokens[t][0].isupper()):
            chainCapitalized = False

        if(cntUpper/float(len(whole_sentence)) > 0.25):
#            feats_per_position[t].add("mostInUpper")
            pass 
        else: 
#            cntLower = sum(1 for c in whole_sentence if c[0].islower())
#            if(INITCAP.match(tokens[t]) 
            if(tokens[t][0].isupper()
                #and cntLower/float(len(whole_sentence)) > 0
                ):
                feats_per_position[t].add("initcap") #TODO: here only activate when most of the words in the sentence
                if(chainCapitalized):
                    pass 
#                    feats_per_position[t].add("chainCapitalized")

                if(t>0 and tokens[t-1][0].islower()):
                    feats_per_position[t].add("initcapafterlower")
                    chainCapitalized = True

                if(t>1 and tokens[t-1][0].islower() and tokens[t-2][0].islower()):
                    feats_per_position[t].add("initcapafter2lower")
                    chainCapitalized = True

                if(t>2 and tokens[t-1][0].islower() and tokens[t-2][0].islower() and tokens[t-3][0].islower()):
                    feats_per_position[t].add("initcapafter3lower")
                    chainCapitalized = True

                if(t<N-1 and tokens[t+1][0].islower()):
                    feats_per_position[t].add("initcapbefore1lower")




        wordShape = getWordShape(tokens[t])
        compactWS = getCompactWordShape(wordShape)
        if(compactWS!=''):
            feats_per_position[t].add("wordShape_" + wordShape)
            feats_per_position[t].add("compactwordShape_" + compactWS)

        if(t>0):
            wordShape = getWordShape(tokens[t-1])
            compactWS = getCompactWordShape(wordShape)            
            feats_per_position[t].add("prev_wordShape_" + wordShape)
            feats_per_position[t].add("prev_compactwordShape_" + compactWS)


        if(t<N-1):
            wordShapep = getWordShape(tokens[t+1])
            compactWS = getCompactWordShape(wordShape)            
            feats_per_position[t].add("post_wordShape_" + wordShape)
            feats_per_position[t].add("post_compactwordShape_" + compactWS)


        firstLast1 = getFirstLast(tokens[t],1)
        firstLast2 = getFirstLast(tokens[t],2)
        firstLast3 = getFirstLast(tokens[t],3)
        firstLast4 = getFirstLast(tokens[t],4)
        if(len(firstLast1)>0):
            feats_per_position[t].add("fl1_" + firstLast1)
        if(len(firstLast2)>0):
            feats_per_position[t].add("fl2_" + firstLast2)
        if(len(firstLast3)>0):
            feats_per_position[t].add("fl3_" + firstLast3)
        if(len(firstLast4)>0):
            feats_per_position[t].add("fl4_" + firstLast4)
        if(t>0):
            firstLast1b = getFirstLast(tokens[t-1],1)
            firstLast2b = getFirstLast(tokens[t-1],2)
            firstLast3b = getFirstLast(tokens[t-1],3)
            firstLast4b = getFirstLast(tokens[t-1],4)

            feats_per_position[t].add("prev_fl_1_ %s" % firstLast1b)
            feats_per_position[t].add("prev_fl_2_ %s" % firstLast2b)
            feats_per_position[t].add("prev_fl_3_ %s" % firstLast3b)
            feats_per_position[t].add("prev_fl_4_ %s" % firstLast4b)

        if(t<N-1):
            firstLast1b = getFirstLast(tokens[t+1],1)
            firstLast2b = getFirstLast(tokens[t+1],2)
            firstLast3b = getFirstLast(tokens[t+1],3)
            firstLast4b = getFirstLast(tokens[t+1],4)

            feats_per_position[t].add("post_fl_1_ %s" % firstLast1b)
            feats_per_position[t].add("post_fl_2_ %s" % firstLast2b)
            feats_per_position[t].add("post_fl_3_ %s" % firstLast3b)
            feats_per_position[t].add("post_fl_4_ %s" % firstLast4b)
    return feats_per_position

extract_features_for_sentence = extract_features_for_sentence1

def extract_features_for_file(input_file, output_file):
    """This runs the feature extractor on input_file, and saves the output to
    output_file."""
    sents = read_file(input_file)
    with open(output_file,'w') as output_fileobj:
        for tokens,goldtags in sents:
            feats = extract_features_for_sentence(tokens)
            for t in range(len(tokens)):
                feats_tabsep = "\t".join(feats[t])
                print>>output_fileobj, "%s\t%s" % (goldtags[t], feats_tabsep)
            print>>output_fileobj, ""


def getString(nr_tokens,tokens,idx):
    text_to_analyze = ""
    if(nr_tokens > idx+1):
        return " ".join(tokens[0:idx+1])
    else: 
        return " ".join(tokens[idx + 1 - nr_tokens: idx+1])

def getStringV2(nr_tokens,tokens,idx, offset):
    text_to_analyze = ""
    if(nr_tokens > idx+1+offset):
        return " ".join(tokens[0+offset:idx+1+offset])
    else: 
        return " ".join(tokens[idx + 1 - nr_tokens + offset: idx+1+offset])


def markFeats(nr_tokens, tokens, idx, value):
    start = 0
    end = 0 
    if(nr_tokens > idx+1):
        start = 0 
        end = idx
    else: 
        start = idx + 1 - nr_tokens
        end = idx 
    for i in range(start, end + 1):
        tokens[i].add(value)


def checkNationalPlaces(text): 
    return (text.lower().strip() in loadedNationalPlaces)


def checkArtifact(text): 
    text = text.strip().replace(' ', '_')
    stopLooping = 0 
    i = 1
    while(stopLooping==0):
        try:
            move_synset = S(text + '.n.' + str(i))
            if(
                move_synset.lexname() == 'noun.artifact'

                ):
                return 1 
            i = i+1
        except:
            stopLooping = 1
    return 0 

def checkLocation(text):
    text = text.strip().replace(' ', '_')
    stopLooping = 0 
    i = 1
    while(stopLooping==0):
        try:
            move_synset = S(text + '.n.' + str(i))
            if(
                move_synset.lexname() == 'noun.location'

                ):
                return 1 
            i = i+1
        except:
            stopLooping = 1
    return 0 

def checkObject(text):
    text = text.strip().replace(' ', '_')
    stopLooping = 0 
    i = 1
    while(stopLooping==0):
        try:
            move_synset = S(text + '.n.' + str(i))
            if(move_synset.lexname() == 'noun.object'):
                return 1 
#            print "LOCATION: " + str(text)
            i = i+1
        except:
            stopLooping = 1
    return 0 

def checkPerson(text):
    text = text.strip().replace(' ', '_')
    stopLooping = 0 
    i = 1
    while(stopLooping==0):
        try:
            move_synset = S(text + '.n.' + str(i))
            if(move_synset.lexname() == 'noun.person'):
                return 1 
            i = i+1
        except:
            stopLooping = 1
    return 0 

def getWordShape(token):
    ws = '' 
    if(token[0] in ('@','#')):
        return '' 
    for c in token:
        if c.isdigit(): 
            ws = ws + 'D'
        elif c.islower(): 
            ws = ws + 'L'
        elif c.isupper(): 
            ws = ws + 'U'
        elif c in ('.',',',';', ':', '?', '!'): 
            ws = ws + '.'
#        elif c in ('-'): 
#            ws = ws + '-'
        elif c in ('+', '*', '/', '=', '|', '_', '{', '[', '<', '}', ']', '>' ): 
            ws = ws + '_'
#        elif c in ('('):
#            ws = ws + '('
#        elif c in (')'):
#            ws = ws + ')'
        else:
            ws = ws + c

    return ws 

def paddFirstLast(token,size): 
    paddedWord = token
    while(not (size*2 <= len(paddedWord)) and 
        not (size*2-1 <= len(paddedWord) and len(paddedWord)%2==1)
        ):
        paddedWord = "^" + paddedWord + "$"    
    return paddedWord

def getFirstLast(token,size):
#    if(token[0]=='#' or token[0]=='@'):
#        return "" 
    padded = paddFirstLast(token,size)

    if(size*2 <= len(padded)):
        toreturn = "flfeature_" + padded[0:size].lower() + "_" + padded[len(padded)-size:len(padded)].lower()
        return toreturn
    elif (size*2-1 <= len(padded) and len(padded)%2==1):
        toreturn = "flfeature_" + padded[0:size].lower() + "_" + padded[len(padded)-size:len(padded)].lower()
        return toreturn
    else:
        print "ERROR, SHOULDN'T BE HERE"
        return ""

def getCompactWordShape(ws): 
    prevWordShape = '' 
    compactWS = '' 
    for c in ws: 
        if(c!=prevWordShape): 
            compactWS = compactWS + c 
            prevWordShape = c 

    return compactWS

extract_features_for_file("train_and_dev.txt", "train_and_dev.feats")
#extract_features_for_file("dev.txt", "dev.feats")
#extract_features_for_file("train_and_dev.txt", "train_and_dev.feats")
extract_features_for_file("test_withlabels.txt", "test_withlabels.feats")
