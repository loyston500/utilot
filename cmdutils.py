PIPE = 124
FILE = 62
COLN = 59
EVAL = 69

FILEOUT = 4962
FILEERR = 5062

def tokenize(string):
    chars = list(string.strip())
    i = 0
    tokens = []
    temp = []
    
    while i < len(chars):
        c = chars[i]
        
        if c == '\\':
            temp.append(chars[i + 1])
            i += 1
        
        elif c in ('>', '|', ';'):
            if temp:
                tokens.append(''.join(temp))
                temp = []
            tokens.append(ord(c))
            
        elif c == ' ':
            if temp:
                tokens.append(''.join(temp))
                temp = []
                
        elif c in ("'", '"'):
            i += 1
            try:
                if chars[i] == c:
                    temp.append(c)
                    temp.append(c)
                else:
                    while chars[i] != c:
                        temp.append(chars[i])
                        i += 1
            except IndexError as err:
                raise err
            
        else:
           temp.append(c)
        
        i += 1
    
    if j := ''.join(temp):
        tokens.append(''.join(temp))

    if tokens[-1] != COLN:
        tokens.append(COLN)

    return tokens

def tree(tokens):
    temp = []
    tree = []
    i = 0
    
    if tokens[-1] != COLN:
        tokens.append(COLN)
    
    while i < len(tokens):
        if tokens[i] in (PIPE, COLN, FILE, FILEOUT, FILEERR):
            if temp:
                tree.append(temp)
                temp = []
            tree.append(tokens[i])
        else:
            temp.append(tokens[i])
        
        i += 1
    
    return tree

def parse(tokens):
    i = 0
    colncount = 0
    pipecount = 0
    filecount = 0
    instrs = []
    
    while i < len(tokens):
        if tokens[i] == COLN:
            assert type(tokens[i - 1]) == list
            
            instrs.append([COLN])
            i += 1
            
            colncount += 1
            
        elif tokens[i] == PIPE:
            assert type(tokens[i + 1]) == list
            
            instrs.append([PIPE, tokens[i + 1]])
            i += 2
            
            pipecount += 1
            
        elif tokens[i] in (FILE, FILEOUT, FILEERR):
            assert type(tokens[i + 1]) == list
            
            instrs.append([tokens[i], tokens[i + 1][0]])
            i += 2
            
            filecount += 1 
            
        else:
            instrs.append([EVAL, tokens[i]])
            i += 1
        
    return instrs, (colncount, pipecount, filecount)
            
    
    
    
    
    
