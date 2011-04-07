import time
import json
import sys
import pkg_resources
import os

from pattern.web import cache

import feed
import metrics

def start(configfile):
    config = open(configfile, 'r')
    feedlist = json.loads(config.read())
    config.close()

    DELAY = 3600 #one hour
    DAY = 24

    datapath = 'data/'
    logdir = 'logs/'

    while True:   
        timestr = str(time.time())
        logpath = os.path.join(datapath, logdir)
        if not os.path.exists(logpath):
            os.makedirs(logpath)
        logname = os.path.join(logpath,'news-'+timestr+'.json')
        log = open(logname,'w')

        print timestr + ' starting a new day'
        for i in range(DAY):
            cache.clear()
            
            topics = feed.extract_topics(feedlist)
            topics = filter(metrics.isnews, topics)
            topics = map(lambda x: (x, metrics.gnews_polarity(x)), topics)

            data = (time.time(), topics)
            datastring = json.dumps(data)
            
            log.write(datastring + "\n")
            log.flush()
            print datastring
            
            time.sleep(DELAY)
        log.close()


if __name__ == '__main__':
    #Pattern 1.6 changes stuff and breaks things
    assert pkg_resources.get_distribution('pattern').version == '1.5'
    if not len(sys.argv) == 2:
        print 'Usage: python scraper.py <feedfile>, using default'
        start('feeds.json')
    else:
        start(sys.argv[1])
    
    
