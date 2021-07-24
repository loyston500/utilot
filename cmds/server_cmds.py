from cmd import cmd
import argutils; from argutils import ArgParse

@cmd.new()
@ArgParse.wrap(
    ArgParse()
        .add_argument(names=['u', 'banner-url'], greedy=False)
        
        .test("-u lol".split())
)
async def guild(snd, ctx, piped, args):
    
    kwargs, args = args.parse()
    
    if 'banner_url' in kwargs:
        snd.sendout(str(ctx.guild.banner_url))
    #elif ''
