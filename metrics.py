import urllib
import re
from pattern.web import Wikipedia, Google, NEWS, Newsfeed
from pattern.en import split, parse, wordnet

def sentiment(content):
    if len(wordnet.sentiment) == 0:
        wordnet.sentiment.load()
        
    relevant_types = ['JJ', 'VB', 'RB'] #adjectives, verbs, adverbs
    score = 0
    sentences = split(parse(content))
    for sentence in sentences:
        for word in sentence.words:
            if word.type in relevant_types:
                try:
                    synset = wordnet.synsets(word.string, word.type)[0].weight
                    pos, neg, obj = synset
                except KeyError:
                    #incorrect part of speech tag
                    continue
                score = score + ((pos - neg) * (1 - obj))
    return score

def normalize(s):
    return re.sub('\W',' ', s)

def heuristic_scrape(article):
    from pattern.web import URL, Document, HTTP404NotFound, URLError, plaintext
    try:
        s_content = URL(article).download(timeout=120)
    except (URLError, HTTP404NotFound):
        print "Error downloading", article
        return None

    dom = Document(s_content)
    
    text = ''

    for node in dom.by_tag('p'):
        for c in node:
            if c.type == 'text':
                text = text + ' ' + plaintext(c.source())
    return text.strip()

##Wikipedia, the poor man's ontology
def isnews(topic):
    engine = Wikipedia()
    result = engine.search(topic)
    if result:
        if topic.lower() not in result.title.lower():
            return False
        newsthings = ['places','cities','capitals','countries','people','wars']
        categories = result.categories
        for category in categories:
            for thing in newsthings:
                if thing in category.lower():
                    return True
        return False
    else:
        return False

def gnews_hits(topic):
    engine = Google()
    results = engine.search(topic, type=NEWS)
    return results.total

def gnews_polarity(topic):
    engine = Google()
    results = engine.search(topic, type=NEWS)
    score = 0
    #only 8 results without using paging/cursor
    for result in results:
        content = heuristic_scrape(urllib.unquote(result.url))
        if content:
            polarity = sentiment(normalize(content))
            score = score + polarity
        else:
            results.remove(result)
    return score / float(len(results)) #avg sentiment
