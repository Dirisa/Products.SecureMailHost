"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

This script (C) by Lalo Martins, lalo@laranja.org

License: see LICENSE.txt

$Id: migrate_cmfcol.py,v 1.1 2004/03/15 21:18:42 lalo Exp $
"""


"""
Migration script for CMFCollector to PloneCollectorNG

ATTENTION:

RUNNING THIS SCRIPT MIGHT DAMAGE YOUR PLONE SITE OR OVERRIDE SETTINGS OF YOUR
PLONE IF NOT APPLIED AND CONFIGURED PROPERLY. RUN THIS SCRIPT AT YOUR OWN RISK.
PERFORM A BACKUP OF YOUR DATA.FS **BEFORE** RUNNING THIS SCRIPT.  DO NOT
COMPLAIN IN CASE OF A FAILURE OR DATA LOSS. YOU HAVE BEEN WARNED!!!!!!!!!!!
"""

from DocumentTemplate import HTML
which_collector_form = HTML('''<dtml-var manage_page_header>
<h1>Migrate which collector?</h1>
<form action="&dtml-URL;">
<select name="collector_path">
<dtml-in collectors>
<option value="&dtml-getPath;"><dtml-var Title>(<dtml-var getURL>)</option>
</dtml-in>
</select>
<br />
Optionally, you may choose an id for the new collector:
<br />
<input name="newid" />
<br />
<input type="submit" value="Ok" />
</form>
<dtml-var manage_page_footer>''')

# public method - this is the one you call from ZMI
def migrate(self, collector_path=None, newid=None):
    collector = None

    if collector_path is None:
        if self.meta_type == 'CMF Collector':
            collector = self
            self = self.aq_parent
        else:
            collectors = self.portal_catalog(meta_type='CMF Collector')
            if not collectors:
                return 'No collectors to migrate'
            if len(collectors) == 1:
                collector = collectors[0].getObject()
            else:
                #for c in collectors:
                #    c.path = 
                return which_collector_form(self, self.REQUEST, collectors=collectors)

    if collector is None:
        collector = self.restrictedTraverse(collector_path)

    _migrate_collector(self, collector, newid)


from Products.PloneCollectorNG.Collector import PloneCollectorNG
from Products.PloneCollectorNG.Issue import PloneIssueNG
from Products.PloneCollectorNG import config
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField, DateTimeField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, IdWidget, StringWidget, CalendarWidget

def _make_unused_id(folder, base):
    used_ids = folder.objectIds()
    counter = 0
    id = base
    while id in used_ids:
        counter += 1
        id = '%s_%s' % (base, counter)
    return id

def _migrate_collector(self, collector, newid):
    resp = self.REQUEST.RESPONSE
    hacked = hasattr(collector, 'software_version_vocab')
             # hacked plone.org Collector (or clone thereof)
    try:
        print >> resp, 'Migrating collector at %r' % (collector.absolute_url())
        dest = collector.aq_parent
        newid = _make_unused_id(dest, newid or 'migrated_' + collector.getId())
        p_collector = PloneCollectorNG(newid)
        print >> resp, 'Created instance: %r' % newid
        p_collector.setTitle(collector.Title())
        p_collector.setDescription(collector.Description())
        p_collector.setParticipation_mode(collector.participation)
        if getattr(collector, 'email', None):
            p_collector.setCollector_email(collector.email)
        if getattr(collector, 'abbrev', None):
            p_collector.setCollector_abbreviation(collector.abbrev)
        print >> resp, 'Migrated basic metadata'
        issue_schema = p_collector.atse_getSchema()
        issue_schema['topic'].vocabulary = DisplayList(zip(collector.topics, collector.topics))
        issue_schema['classification'].vocabulary = DisplayList(zip(collector.classifications,
                                                                    collector.classifications))
        issue_schema['importance'].vocabulary = DisplayList(
            [(i, i.capitalize()) for i in collector.importances])
        issue_schema.addField(
            StringField('version_info',
                        required=0,
                        searchable=1,
                        schemata='issuedata',
                        widget=TextAreaWidget(label="Version information",
                                              label_msgid="label_version_info",
                                              i18n_domain="plone"),
                        default=collector.version_info_spiel
                        ))
        issue_schema.addField(
            StringField('contact_id',
                        searchable=1,
                        required=1,
                        schemata='contact',
                        widget=StringWidget(label='Name',
                                            label_msgid='label_contact_name',
                                            i18n_domain='plonecollectorng'),
                        ))
        if hacked:
            issue_schema.addField(
                StringField('software_version',
                            required=1,
                            searchable=1,
                            createindex=1,
                            schemata='issuedata',
                            widget=SelectionWidget(format='select',
                                                   label='Target version',
                                                   label_msgid='label_software_version',
                                                   i18n_domain='plone'),
                            vocabulary=DisplayList(zip(collector.software_version_vocab,
                                                       collector.software_version_vocab)),
                            default=collector.default_software_version,
                            # on request by limi:
                            write_permission = config.ManageCollector,
                            ))
        print >> resp, 'Migrated issue schema'
        dest._setObject(newid, p_collector)
        p_collector = getattr(dest, newid)
        del dest
        print >> resp, 'Stuck it in the ZODB'
        p_collector.set_staff(managers=collector.managers, supporters=collector.supporters)
        print >> resp, 'Migrated staff'
        p_collector.set_notification_emails(collector.state_email)
        print >> resp, 'Migrated notification emails'
        issues = collector.objectValues(['CMF Collector Issue'])[1:]
        print >> resp, 'Ready to migrate %r issues' % len(issues)
        for issue in issues:
            _migrate_issue(issue, collector, p_collector, resp, hacked)
    except:
        import traceback
        traceback.print_exc(file=resp)
        raise

def _migrate_issue(issue, collector, p_collector, resp, hacked):
    issue_id = p_collector.add_issue()
    print >> resp, 'Migrating issue %s to %s' % (issue.getId(), issue_id)
    p_issue = getattr(p_collector, issue_id)
    print >> resp, '  created...'
    p_issue.update(
        title = issue.Title(),
        description = issue.Description(),
        classification = issue.classification,
        topic = issue.topic,
        importance = issue.importance,
        version_info = issue.version_info,
        contact_name = issue.submitter_name,
        contact_email = issue.submitter_email,
        software_version = getattr(issue, 'software_version', None),
    )
    print >> resp, '  Migrated basic information'
