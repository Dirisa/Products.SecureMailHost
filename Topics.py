"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 Tübingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: Topics.py,v 1.8 2004/11/12 15:37:52 ajung Exp $
"""


from Globals import InitializeClass, Persistent
from BTrees.OOBTree import OOBTree
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import *

from config import ManageCollector

class Topics(Persistent):
    """ A wrapper to handle the topic->users mapping """
    
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self):
        self.clear()

    security.declareProtected(ManageCollector, 'clear')
    def clear(self):
        self._topics = []
        self._topic_user = OOBTree()  # topic - > [users]
    
    security.declareProtected('View', 'getTopics')
    def getTopics(self):
        """ return list of topics """
        lst = self._topics
        lst.sort()        
        return lst

    security.declareProtected('View', 'getTopicsForUser')
    def getTopicsForUser(self, user):
        """ get a list of topics for a particular user """
        return [t for t,users in self._topic_user.items() if user in users]

    security.declareProtected('View', 'getUsersForTopic')
    def getUsersForTopic(self, topic):
        """ return all users for a particular topic """
        return list(self._topic_user[topic])

    security.declareProtected(ManageCollector, 'deleteTopic')
    def deleteTopic(self, topic):
        """ delete a topic""" 
        self._topics.remove(topic)
        del self._topic_user[topic]
        self._p_changed = 1

    security.declareProtected(ManageCollector, 'addTopic')
    def addTopic(self, topic):
        """ add a topic """
        if topic in self._topics:
            raise ValueError(self.Translate('topic_exiists', 'Topic $topic already exists', topic=topic))
        self._topics.append(topic)
        self._topic_user[topic] = []
        self._p_changed = 1

    security.declareProtected(ManageCollector, 'addUser')
    def addUser(self, topic, user):
        """ add a user to a topic """
        if not user in self._topic_user[topic]:
            self._topic_user.append(user)
        self._p_changed = 1
    
    security.declareProtected(ManageCollector, 'setUsers')
    def setUsers(self, topic, users):
        """ set users for a topic """
        self._topic_user[topic] = users
        self._p_changed = 1

    security.declareProtected(ManageCollector, 'deleteUser')
    def deleteUser(self, topic, user):
        """ delete a user from a topic """
        if not topic in self._topics:
            raise ValueError(self.Translate('no_such_topic', 'No such topic $topic', topic=topic))
        if user in self._topic_user[topic]:
            self._topic_user.remove(user)
        self._p_changed = 1

InitializeClass(Topics) 

