"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: notification_policies.py,v 1.1 2003/10/11 20:45:07 ajung Exp $
"""

class BasePolicy:

    def __init__(self, issue):
        self.issue = issue
        self.r = {'submitter' : {'email': issue.contact_email}}
        self.collector = self.issue._getCollector()

    def getRecipients(self):
        raise NotImplementError


def NoneNotificationPolicy(BasePolicy):
    """ no notifications """

    def getRecipients(self):
        return {}


def SupportersNotificationPolicy(BasePolicy):
    """ Submitter, all supporters and tracker administrators """
    
    def getRecipients(self):
        for uid in self.collector._managers: self.r[uid] = {}   # all managers
        for uid in self.collector._supporters: self.r[uid] = {} # all supporters
        return r


def AssignedSupportersNotificationPolicy(BasePolicy):
    """ Submitter, assigned supporters and tracker administrators """

    def getRecipients(self):
        for uid in self.collector._managers: self.r[uid] = {}   # all managers
        for uid in issue.assigned_to(): self.r[uid] = {}        # all assignees
        return self.r


from Products.Archetypes.public import DisplayList

def VOC_NOTIFICATION_POLICIES(): 
    """ return DisplayList instance for collector_schema """

    d = []
    for klass in (NoneNotificationPolicy, SupportersNotificationPolicy, 
                  AssignedSupportersNotificationPolicy):
        d.append([klass.__name__, klass.__doc__])
    return DisplayList(d)

