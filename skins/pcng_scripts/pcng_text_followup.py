##parameters=timestamp

# Search through all transcript events for a comment with the given
# timestamp (passed as float) and return a ">" quoted strings that
# will used for followups.

def quote_text(text):
    lines = context.wrap_text(text).split('\n')
    lines = [':' + l for l in lines]
    return '\n'.join(lines)

for ev in context.getTranscript().getEvents():
    if ev.getType() == 'comment' and str(ev.getTimestamp()) == str(timestamp):
        text = context.Translate('followup_heading', 'Created by $user on $date', 
                                 date=context.toLocalizedTime(DateTime(ev.getTimestamp()), long_format=1), 
                                 user=ev.getUser())
        text += '\n\n'
        text += quote_text(ev.getValue('comment'))
        return text
        
return timestamp
