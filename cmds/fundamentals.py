from cmd import cmd
import argutils; from argutils import ArgParse

@cmd.new()
async def merge(snd, ctx, piped, args):
    '''
    whatis: 'merges out and err to one single out'
    man:
        props:
            - PIPED ONLY [any]
            - GREEDY
            - FUNDAMENTAL
        description: >
            No direct usage.
            Can only be piped.
        examples:
            - |
                whatis cb blah | {name} | echo
    '''
    
    if piped:
        snd._out.extend(piped._out)
        snd._out.extend(piped._err)
        
@cmd.new(name='try')
async def _try(snd, ctx, piped, args):
    '''
    whatis: 'stops the execution if any exitcode other than 0 is received'
    man:
        props:
            - PIPED ONLY
            - GREEDY
            - FUNDAMENTAL
        description: >
            Stops the execution by passing exit code
            200 if the received exit code is anything
            other than 0.
        examples:
            - |
                whatis cb blah | {name} | bold
    '''
    if piped:
        snd._out = piped._out
        snd._err = piped._err
        if piped._exitcode != 0:
            snd.exitcode(200)
        else:
            snd.exitcode(0)


@cmd.new()
@ArgParse.wrap(
    ArgParse()
        .add_argument(names=["f", "foo"], optional=True, default="foo default", greedy=True)
        .add_argument(names=["b", "bar"], optional=True, default="bar default", greedy=True)
        .add_argument(names=["k", "kar"], optional=True, greedy=True)
        
        .test("-f foolol -b lol".split())
)
async def argtest(snd, ctx, piped, args):
    args, left = args.parse()
    
    snd.sendout(f"{args = }\n{left = }")
    
    
    
    
