# return a mapping userid -> list of topicgroups


d = {}

for topic, users in context.get_topics_user().items():
    
    for user in users:
        if not d.has_key(user): d[user] = []
        d[user].append(topic)

return d    

