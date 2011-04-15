import heapq
import operator
from pattern.vector import Document, LEMMA
from pattern.web import Newsfeed

def article_titles(feeds):
    titles = {}
    for key in feeds:
        titles[key] = []
        newsfeed = Newsfeed().search(feeds[key])
        for result in newsfeed:
            titles[key].append(result.title)
    return titles

def documents_from_feeds(feeds):
    titles = article_titles(feeds)
    documents = []
    for key in titles:
        doc = Document(" ".join(titles[key]), stemmer=LEMMA, threshold=0)
        documents.append(doc)
    return documents

def extract_topics(feeds):
        
    documents = documents_from_feeds(feeds)
    topicsets = []
    
    for doc in documents:
        words = []
        #lowercasing in pattern 1.6 changes keywords results
        for tup in doc.keywords(top=30):
            words.append(str(tup[1]).decode('utf-8'))
        topicsets.append(words)

    topdict = {}
    for topiclist in topicsets:
        for topic in topiclist:
            try:
                topdict[topic] = topdict[topic] + 1
            except KeyError:
                topdict[topic] = 0

    highest = heapq.nlargest(10, topdict.iteritems(), operator.itemgetter(1))

    topics = []
    for key in highest:
        topstr = key[0]
        if(topstr.endswith('um')):
            #The stemmer thought these were Latin plurals
            topstr = topstr.replace('ium','ia') #eg Syria, Russia
            topstr = topstr.replace('atum','ata') #eg Misrata
        topics.append(topstr)

    return topics
