"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Topics.py,v 1.2 2004/10/09 15:19:30 ajung Exp $
"""


from Globals import InitializeClass, Persistent
from BTrees.OOBTree import OOBTree, difference, OOSet
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import *

from config import ManageCollector

class Topics(Persistent):
    
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self):
        self.clear()

    def clear(self):
        self._topics = []
        self._topic_user = OOBTree()  # topic - > [users]
    
    def getTopics(self):
        """ return list of topics """
        return self._topics

    def getTopicsForUser(self, user):
        """ get a list of topics for a particular user """
        return [t for t,users in self._topic_user.items() if user in users]

    def getUsersForTopic(self, topic):
        """ return all users for a particular topic """
        return list(self._topic_user[topic])

    def deleteTopic(self, topic):
        """ delete a topic""" 
        self._topics.remove(topic)
        del self._topic_user[topic]

    def addTopic(self, topic):
        """ add a topic """
        if not topic in self._topics:
            self._topics.append(topic)
        self._topic_user[topic] = []

    def addUser(self, topic, user):
        """ add a user to a topic """
        if not user in self._topic_user[topic]:
            self._topic_user.append(user)

    def deleteUser(self, topic, user):
        """ delete a user from a topic """
        if user in self._topic_user[topic]:
            self._topic_user.remove(user)

InitializeClass(Topics) 

