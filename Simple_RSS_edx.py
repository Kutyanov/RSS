# edx 6.00x 
# RSS Feed Filter

import feedparser
import string
import time
from project_util import translate_html
from Tkinter import *


# Code for retrieving and parsing RSS feeds from Google and Yahoo News


def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        summary = translate_html(entry.summary)
        try:
            subject = translate_html(entry.tags[0]['term'])
        except AttributeError:
            subject = ""
        newsStory = NewsStory(guid, title, subject, summary, link)
        ret.append(newsStory)
    return ret

class NewsStory (object):
    """
    This class stores needed attributes and methods.
    """
    def __init__ (self, Guid, Title, Subject, Summary, Link):
		self.Guid = Guid
		self.Title = Title
		self.Subject = Subject
		self.Summary = Summary
		self.Link = Link
	
    def getGuid(self):
		return self.Guid
	
    def getTitle(self):
		return self.Title
	
    def getSubject(self):
		return self.Subject
		
    def getSummary(self):
		return self.Summary
		
    def getLink(self):
		return self.Link


# Triggers


class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        raise NotImplementedError


# Whole Word Triggers


class WordTrigger(Trigger):
    """
    This trigger checks if the whole world in text.
    """
    def __init__(self, word):
        self.word = word.lower()

    def isWordIn(self, text):
        sample = string.punctuation
        for i in sample:
            text = text.replace(i,' ')
        text = text.lower()
        text = text.split(' ')
        return self.word in text
   
            

class TitleTrigger(WordTrigger):
    """
    Title trigger fires when a news item's title contains a given word
    """
    def evaluate(self, story):
        return self.isWordIn(story.getTitle())
        


class SubjectTrigger(WordTrigger):
    """
    This trigger fires when a news item's subject contains a given word.
    """
    def evaluate(self, story):
        return self.isWordIn(story.getSubject())
    
    

class SummaryTrigger(WordTrigger):
    """
    This trigger fires when a news item's summary contains a given word.
    """
    def evaluate(self, story):
        return self.isWordIn(story.getSummary())


# Composite Trigger


class NotTrigger(Trigger):
    """
    This trigger should produce its output by inverting the output of another trigger.
    """
    def __init__(self, Trigger):
		self.Trigger = Trigger
	
    def evaluate(self, story):
		return not self.Trigger.evaluate(story)
		
class AndTrigger(Trigger):
    """
    This trigger should take two triggers as arguments to its constructor, 
    and should fire on a news story only if both of the inputted triggers 
    would fire on that item.
    """
    def __init__ (self, Trigger_1, Trigger_2):
		self.Trigger_1 = Trigger_1
		self.Trigger_2 = Trigger_2
    def evaluate (self, story):
		if self.Trigger_1.evaluate(story) == True and self.Trigger_2.evaluate(story) == True:
			return True
		return False
		
class OrTrigger(Trigger):
    """
    This trigger should take two triggers as arguments to its constructor, 
    and should fire if either one (or both) of its inputted triggers 
    would fire on that item.
    """
    def __init__ (self, Trigger_1, Trigger_2):
		self.Trigger_1 = Trigger_1
		self.Trigger_2 = Trigger_2
    def evaluate (self, story):
		if self.Trigger_1.evaluate(story) == True or self.Trigger_2.evaluate(story) == True:
			return True
		return False

class PhraseTrigger(Trigger):
    """
    This trigger fires when a given phrase is in any of the story's subject, title, or summary.
    """
    def __init__ (self, phrase):
		self.phrase = phrase
		
    def evaluate(self, text):
		return self.phrase in text.getTitle() or self.phrase in text.getSubject() or self.phrase in text.getSummary()


# Filtering


def filterStories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    newList = []
    for i in triggerlist:
        for j in stories:
            if i.evaluate(j) == True:
                newList.append(j)
    return newList


# User-Specified Triggers


def makeTrigger(triggerMap, triggerType, params, name):
    """
    Takes in a map of names to trigger instance, the type of trigger to make,
    and the list of parameters to the constructor, and adds a new trigger
    to the trigger map dictionary.

    triggerMap: dictionary with names as keys (strings) and triggers as values
    triggerType: string indicating the type of trigger to make (ex: "TITLE")
    params: list of strings with the inputs to the trigger constructor (ex: ["world"])
    name: a string representing the name of the new trigger (ex: "t1")

    Modifies triggerMap, adding a new key-value pair for this trigger.

    Returns: None
    """
    if triggerType=='TITLE':
        triggerMap[name]=TitleTrigger(params[0])
    elif triggerType == 'SUBJECT':
        triggerMap[name]=SubjectTrigger(params[0])
    elif triggerType == 'SUMMARY':
        triggerMap[name]=SummaryTrigger(params[0])
    elif triggerType == 'AND' :
        triggerMap[name] =AndTrigger( triggerMap[params[0]], triggerMap[params[1]])
    elif triggerType == 'OR':
        triggerMap[name] = OrTrigger( triggerMap[params[0]],triggerMap[params[1]])
    elif triggerType == 'NOT':
        triggerMap[name]= NotTrigger(triggerMap[params[0]])
    elif triggerType == 'PHRASE':
        triggerMap[name]=PhraseTrigger(' '.join(params))
    return  triggerMap[name]


def readTriggerConfig(filename):
    """
    Returns a list of trigger objects
    that correspond to the rules set
    in the file filename
    """

    # Here's some code that we give you
    # to read in the file and eliminate
    # blank lines and comments
    triggerfile = open('triggers.txt', "r")
    all = [ line.rstrip() for line in triggerfile.readlines() ]
    lines = []
    for line in all:
        if len(line) == 0 or line[0] == '#':
            continue
        lines.append(line)

    triggers = []
    triggerMap = {}

    # Be sure you understand this code - we've written it for you,
    # but it's code you should be able to write yourself
    for line in lines:

        linesplit = line.split(" ")

        # Making a new trigger
        if linesplit[0] != "ADD":
            trigger = makeTrigger(triggerMap, linesplit[1],
                                  linesplit[2:], linesplit[0])

        # Add the triggers to the list
        else:
            for name in linesplit[1:]:
                triggers.append(triggerMap[name])
    return triggers
    
import thread

SLEEPTIME = 60 #seconds -- how often we poll


	

def main_thread(master):
    # A sample trigger list - you'll replace
    # this with something more configurable in Problem 11
    try:
        triggerlist = readTriggerConfig("triggers.txt")

        # from here is about drawing
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.getGuid() not in guidShown:
                cont.insert(END, newstory.getTitle()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.getSummary())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.getGuid())

        while True:

            print "Polling . . .",
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/?output=rss")

            # Get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://rss.news.yahoo.com/rss/topstories"))

            stories = filterStories(stories, triggerlist)

            map(get_cont, stories)
            scrollbar.config(command=cont.yview)


            print "Sleeping..."
            time.sleep(SLEEPTIME)

    except Exception as e:
        print e


if __name__ == '__main__':

    root = Tk()
    root.title("Simple RSS parser")
    thread.start_new_thread(main_thread, (root,))
    root.mainloop()

