
# Migrate transcripts for all issues to unicode

encoding = context.getSiteEncoding()

print 'Migrating issue transcripts to unicode'

for issue in context.objectValues('PloneIssueNG'):
    issue.getTranscript().setEncoding(encoding)
    issue.getTranscript().migrateUnicode()
    print 'Issue #', issue.getId(), 'migrated'

return printed
