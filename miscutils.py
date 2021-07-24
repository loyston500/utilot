def fmt(string, prefix, **kwargs):
    for key, value in kwargs.items():
        string = string.replace(prefix + key, str(value))
    
    return string

def pointer(
    msg=None, 
    char_limit=20, 
    cb=True, 
    lang="py",
    frm=10,
    to=10, 
    extra="", 
    position=0, 
    prefix="", 
    pad="~", 
    pointer="^",
    pl=0,
    ):
    if msg is None:
        ptr_string = prefix + (pad * (position + pl - len(prefix))) + pointer + extra
        return ptr_string

    trimmed = msg
    pad_count = position - len(prefix)
    if len(msg) > char_limit:
        trimmed = msg[position - frm: position + to]
        pad_count = frm
        
    pre, suf = "", ""
    if cb:
        pre = "```" + lang + "\n"
        suf = "\n```"

    ptr_string = prefix + (pad * pad_count) + pointer + extra

    return f"{pre}{trimmed}\n{ptr_string}{suf}"
