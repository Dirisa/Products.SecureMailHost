"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: notification_policies.py,v 1.6 2003/11/01 17:03:25 ajung Exp $
"""

""" 
This module implements some basic policies used by the email 
notification mechanism to determine the list of recipients.
"""

class BasePolicy:
    """ Base class for all notification policies. By default we include
        the submitter, all managers and all watchers. The recipients are
        stored as a mapping where the key is either the UID of a recipient
        or the email address and value is a dictionary that contains other
        metadata. The email address is stored under the key 'email'. 
    """
    def __init__(self, issue):
        self.issue = issue
        self.collector = self.issue._getCollector()

        # submitter
        self.r = {'submitter' : {'email': issue.contact_email}}

        # all watchers 
        for email in issue.wl_getWatchers():
            self.r[email] = {'email': issue.contact_email}

        # special notifications based on the state
        for email in self.collector.getNotificationsForState(issue.status()):
            print email
            self.r[email] = {'email': email}

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
        for uid in self.issue.assigned_to(): self.r[uid] = {}        # all assignees
        return self.r


from Products.Archetypes.public import DisplayList

def VOC_NOTIFICATION_POLICIES(): 
    """ return DisplayList instance for collector_schema """

    return DisplayList([ [klass.__name__, klass.__doc__]
                          for klass in (NoneNotificationPolicy, 
                                        SupportersNotificationPolicy, 
                                        AssignedSupportersNotificationPolicy)
                       ])

