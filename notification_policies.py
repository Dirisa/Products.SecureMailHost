"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: notification_policies.py,v 1.3 2003/10/12 19:34:28 ajung Exp $
"""

""" 
This module implements some basic policies used by the email 
notification mechanism to determine the list of recipients.
"""

class BasePolicy:

    def __init__(self, issue):
        self.issue = issue
        self.collector = self.issue._getCollector()

        # submitter
        self.r = {'submitter' : {'email': issue.contact_email}}

        # all watchers 
        for email in issue.wl_getWatchers():
            self.r[email] = {'email': issue.contact_email}

        # all managers
        for uid in self.collector._managers: 
            self.r[uid] = {}   
    
    def clear(self):
        self.r = {}

    def getRecipients(self):
        raise NotImplementError


class NoneNotificationPolicy(BasePolicy):
    """ no notifications """

    def getRecipients(self):
        return {}


class SupportersNotificationPolicy(BasePolicy):
    """ Submitter, all supporters and tracker administrators """
    
    def getRecipients(self):
        for uid in self.collector._supporters: self.r[uid] = {} # all supporters
        return self.r


class AssignedSupportersNotificationPolicy(BasePolicy):
    """ Submitter, assigned supporters and tracker administrators """

    def getRecipients(self):
        for uid in issue.assigned_to(): self.r[uid] = {}        # all assignees
        return self.r


from Products.Archetypes.public import DisplayList

def VOC_NOTIFICATION_POLICIES(): 
    """ return DisplayList instance for collector_schema """

    return DisplayList([ [klass.__name__, klass.__doc__]
                          for klass in (NoneNotificationPolicy, 
                                        SupportersNotificationPolicy, 
                                        AssignedSupportersNotificationPolicy)
                       ])

