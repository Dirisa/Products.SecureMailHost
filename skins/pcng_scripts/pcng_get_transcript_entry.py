##parameters=timestamp

# Return a timescript entry by timestamp

for ev in context.getTranscript().getEvents():
    if ev.getType() == 'comment' and str(ev.getTimestamp()) == str(timestamp):
        return ev.getComment()
        
raise ValueError('No comment found for given timestamp....this should never happen')

 
