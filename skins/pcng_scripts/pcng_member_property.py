##parameters=member,property,default=None

if default is None:
    value = member.getProperty(property)
else:
    value = member.getProperty(property, default)

if not value and default is not None:
    return default
else:
    return value


