from cmd import cmd
import argutils; from argutils import ArgParse
from miscutils import fmt
import gzip

tags: dict = {}
default_fmt_string = 'length=$LENGTH compressed=$CLENGTH ratio=$RATIOx\n'


@cmd.new()
@ArgParse.wrap(
    ArgParse()
        .add_argument(names=['c', 'create'])
        .add_argument(names=['d', 'delete'])
        .add_argument(names=['i', 'info'], greedy=True)
        .add_argument(names=['f', 'format'], greedy=True)
        
        .test("-c test thisissomethng".split())
        .test("test thisissomething -c ".split(), strict=False)
)
async def tag(snd, ctx, piped, args):
    kwargs, args = args.parse()
    
        
    if 'create' in kwargs:
        if piped and piped._out:
            content = piped._out[0]
        else:
            if not args:
                snd.senderr('content needed')
                snd.exitcode(1)
                return
            content = args[0].encode()
            
        tags[kwargs.create] = gzip.compress(content, 9)
    
    elif 'delete' in kwargs:
        if kwargs.delete not in tags:
            snd.senderr('tag not found')
            snd.exitcode(1)
            return 
        del tags[kwargs.delete]
        
    elif 'info' in kwargs:
        if kwargs.info not in tags:
            snd.senderr('tag not found')
            snd.exitcode(1)
            return 
        
        fmt_string = kwargs.format or default_fmt_string
        compressed = tags[kwargs.info]
        ratio = (length := len(gzip.decompress(compressed))) / (clength := len(compressed))
        
        out = fmt(fmt_string, '$', LENGTH=length, CLENGTH=clength, RATIO=round(ratio, 3))
        
        snd.sendout(out)
    
    elif args:
        if args[0] not in tags:
            snd.senderr('tag not found')
            snd.exitcode(1)
            return 
        
        out = gzip.decompress(tags[args[0]])
        
        snd.sendout(out)
        
    else:
        snd.senderr('invalid usage')
        snd.exitcode(1)
        
        
            
        
    
            
        
