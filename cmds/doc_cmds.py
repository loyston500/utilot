from cmd import cmd

class DocCmds:
    @cmd.new()
    async def whatis(snd, ctx, piped, args):
        if piped and piped._out:
            out = [o.decode('unicode_escape') for o in piped._out]
        else:
            out = args
        for cmdname in out:
            cmdname = str(cmdname)
            try:
                _cmd = cmd.get(cmdname)
            except KeyError:
                snd.senderr(f"{cmdname}: not found.")
                snd.exitcode(1)
            else:
                if _cmd.__doc__:
                    snd.sendout(f"{cmdname}: {_cmd.__doc__.get('whatis', 'not given.')}")
                else:
                    snd.senderr(f"{cmdname}: not given.")
                    
    @cmd.new()
    async def man(snd, ctx, piped, args):
        if piped and piped._out:
            name = piped._out[0].decode('unicode_escape')
        else:
            if len(args) != 1:
                snd.exitcode(1)
                snd.senderr("excess arguments were passed.")
                return
            else:
                name = args[0]
        
        if not cmd.has(name):
            snd.exitcode(1)
            snd.senderr(f"command `{name}` not found")
            return
        
        if not ((doc := cmd.get(name).__doc__) and ('man' in doc)):
            snd.exitcode(1)
            snd.senderr(f"manual for `{name}` not found")
            return
        
        doc = doc['man']
        s = []
        nl = '\n'
        
        s.append(f"name: {doc.get('name', name)}")
        s.append(f"usage: {doc.get('usage', 'not provided.')}")
        s.append(f"prop: {', '.join(doc.get('prop', ['not provided.']))}")
        s.append(f"examples:\n\n{nl.join(doc.get('examples', ['not provided.']))}")
        s.append(f"description:\n\n{doc.get('description', 'not provided.')}")
        
        s = '\n\n'.join(s)
        
        snd.sendout(s)
