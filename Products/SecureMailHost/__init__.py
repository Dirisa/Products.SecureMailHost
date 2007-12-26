import SecureMailHost
import mail

def initialize(context):
    context.registerClass(
        SecureMailHost.SecureMailHost,
        permission='Add secure MailHost objects',
        constructors=(SecureMailHost.manage_addMailHostForm,
                      SecureMailHost.manage_addMailHost),
        icon='www/MailHost_icon.gif',
    )
