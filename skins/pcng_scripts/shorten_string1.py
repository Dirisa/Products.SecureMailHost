##parameters=text, maxlength=40
# shorten a string

if len(text) > maxlength:
    text = text[:maxlength] + "..."
return text
