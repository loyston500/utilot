def fmt(string, prefix, **kwargs):
    for key, value in kwargs.items():
        string = string.replace(prefix + key, str(value))
    
    return string
