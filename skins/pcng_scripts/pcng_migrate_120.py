## Migrate PloneCollectorNG instance to V 1.2.0+

context.update_collector_schema()
context.setup_tools()
context.migrate_issue_workflow_histories()
context.getTranscript().addComment(u'migrated to 1.2.0')
context.reindex_issues()
context.REQUEST.RESPONSE.redirect('pcng_view')
