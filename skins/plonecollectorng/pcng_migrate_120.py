## Migrate PloneCollectorNG instance to V 1.2.0+

context.setup_tools()
context.reindex_issues()
context.update_collector_schema()
context.migrate_issue_workflow_histories()
context.getTranscript().addComment(u'migrated to 1.2.0')
return 'done'
