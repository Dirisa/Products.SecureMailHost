
# Return a list of topic strings
# If a topic contains subtopic e.g. 'XXX/YYY' then only the first part
# before '/' is used.

vocab = context.atse_getSchemaById('PloneIssueNG')['topic'].vocabulary

topics = []

for k,v in vocab.items():
    if k.find('/') > -1:
        k = k.split('/', 1)[0]
    if not k in topics:
        topics.append(k)
topics.sort(lambda x,y: cmp(x.lower(), y.lower()))
return topics
