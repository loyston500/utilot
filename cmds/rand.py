from cmd import cmd
import argutils; from argutils import ArgParse

from random import Random
import secrets

@cmd.new()
@ArgParse.wrap(
    ArgParse()
        .add_argument(names=['c', 'choose'], greedy=False)
        .add_argument(names=['r', 'range'], greedy=False)
        .add_argument(names=['b', 'bits'], greedy=False)
        .add_argument(names=['n', 'number'], greedy=False)
        .add_argument(names=['S', 'seed'], greedy=True)
        .add_argument(names=['F', 'format'], greedy=False)
        
        
        .test('-c 1 2 3 4'.split())
)
async def random(snd, ctx, piped, args):
    random = Random()
    kwargs, args = args.parse()
    
    if kwargs.seed:
        try:
            seed = int(kwargs.seed)
        except Exception as err:
            #$ err str(err)
            snd.senderr('bad seed')
            snd.exitcode(1)
            return 
        else:
            random.seed(seed)
    
    if piped and piped._out:
        choice = random.choice(piped._out)
        snd.sendout(choice)
    
    
    elif 'range' in kwargs:
        try:
            a, b = int(args[0]), int(args[1])
        except Exception as err:
            #$ err str(err)
            snd.senderr('bad usage')
            snd.exitcode(1)
            return
        
        if a > b:
            a, b = b, a
        
        rand = random.randint(a, b)
        snd.sendout(str(rand))
        
    elif 'bits' in kwargs:
        try:
            c = int(args[0])
        except Exception as err:
            #$ err str(err)
            snd.senderr('bad usage')
            snd.exitcode(1)
            return
        
        if c > 1000:
            snd.senderr('given number must be less than or equal to 1000')
            snd.exitcode(1)
            return
        
        bits = random.getrandbits(c)
        
        if 'format' in kwargs:
            out = '%x' % bits
        else:
            out = str(bits)
            
        snd.sendout(out)
        
    elif 'number' in kwargs:
        snd.sendout(str(random.random()))
    
    #elif 'choose' in kwargs:
    else:
        choice = random.choice(args)
        snd.sendout(choice)
            
        
