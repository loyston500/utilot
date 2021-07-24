import config
import builtins
import importlib
import sys

fprint = builtins.print

if not config.debug:
    def newprint(*args, **kwargs):
        pass
    
    builtins.print = newprint
    
def panic(*args, **kwargs):
    print(*args, **kwargs)
    exit(1)
    
#$ panic     
    
def replace(source):
    lines = source.splitlines()
    ret = []
    
    for n, line in enumerate(lines):
        if line.strip().startswith("#$"):
            indent = line.find("#$")
            toks = line[indent + 2:].split()
            l = []
            
            for tok in toks:
                l.append('{' + tok +  ' = }')
            
            l = '; '.join(l)
            line = (" " * indent) + "print(f'[{__file__}:{" + str(n + 1) + "}]', f'" + l + "')"
          
        ret.append(line)
    
    return '\n'.join(ret) 


# obviously not copied from stackoverflow

def __import__(module_name, package=None):
    spec = importlib.util.find_spec(module_name, package)
    source = spec.loader.get_source(module_name)
    new_source = replace(source)
    module = importlib.util.module_from_spec(spec)
    codeobj = compile(new_source, module.__spec__.origin, 'exec')
    exec(codeobj, module.__dict__)
    sys.modules[module_name] = module
    return module
