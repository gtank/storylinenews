'''
Converts my JSON log files to the XML format used by Michael Ogawa's
prototype implementation of the 'storylines' algorithm. See website
http://www.michaelogawa.com/research/storylines/ for more information.
'''

import json
import os
import xml.etree.ElementTree as et
import xml.dom.minidom as minidom

##Returns dictionary of form
##{unix time stamp : [(topic, avg sentiment score)]}
def loadnews(directory):
    graphdict = {}
    for dirpath, dirnames, filenames in os.walk(directory):
        for name in filenames:
            f = open(os.path.join(dirpath, name),'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                data = json.loads(line)
                graphdict[data[0]] = data[1]
    return graphdict

##Extracts only the log entries where something has changed
def extractevents(logdata):
    events = {}
    last = []
    for key in sorted(logdata.iterkeys()):
        data = logdata[key]
        if last == [] or data != last:
            last = data
            events[key] = data
            #print "%s: %s" % (key, data)
    return events

def buildxml(events):
    root = et.Element('file_events')
    for time in sorted(events.iterkeys()):
        data = events[time]
        time = str(int(time))
        for subject in data:
            topic, score = subject
            event = et.SubElement(root, 'event')
            event.set('filename', 'positive' if score > 0 else 'negative')
            event.set('date', time)
            event.set('author', topic)
    return root

##Makes ElementTree output readable
def prettyPrint(element):
    txt = et.tostring(element)
    return minidom.parseString(txt).toprettyxml()

def convert(logdir, outdir):
    logdata = loadnews(logdir)
    events = extractevents(logdata)
    xmltree = buildxml(events)
            
    xmlfile = open(os.path.join(outdir,'storylinenews.xml'), 'w')
    xmlfile.write(prettyPrint(xmltree))
    xmlfile.close()

outdir = 'data/'
logdir = 'data/logs/'

convert(logdir, outdir)

            
