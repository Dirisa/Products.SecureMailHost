# return a list of emails for all users of a collector instance

return ','.join([d['email'] for d in context.pcng_tool.getTrackerUsers(staff_only=1)])
