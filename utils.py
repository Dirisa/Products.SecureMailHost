from Products.CMFCore.interfaces.Discussions import DiscussionResponse as IDiscussionResponse

def discussion_notify(comment_on_object, variables = {}):
    portal = comment_on_object.portal_url.getPortalObject()

    send_from_address = portal.portal_properties.email_from_address
    send_from_name = portal.portal_properties.email_from_name
    
    mt = portal.portal_membership
    if IDiscussionResponse.isImplementedBy(comment_on_object):
        owner = comment_on_object.Creator()
        if owner:
            member = mt.getMemberById(owner)
            if member:
                send_to_address = member.getProperty('email')

                if send_to_address:
                    
                    mail_text = portal.discussion_reply_notify_template(portal, comment_on_object=comment_on_object, send_from_address=send_from_address, send_from_name=send_from_name, send_to_address=send_to_address, **variables)
                    portal.plone_utils._safeSendTo(mail_text, send_to_address, send_from_address)

        parents = comment_on_object.parentsInThread()
        if not parents:
            return
        comment_on_object = parents[0]
            
    owner = comment_on_object.Creator()
    if owner:
        member = mt.getMemberById(owner)
        if member:
            send_to_address = member.getProperty('email')

            if send_to_address:

                mail_text = portal.discussion_notify_template(portal, comment_on_object=comment_on_object, send_from_address=send_from_address, send_from_name=send_from_name, send_to_address=send_to_address, **variables)
                portal.plone_utils._safeSendTo(mail_text, send_to_address, send_from_address)