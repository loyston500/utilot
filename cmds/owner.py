from cmd import cmd
import traceback
from config import ownerids

@cmd.new(name='eval')
async def _eval(snd, ctx, piped, args):
    if ctx.author.id not in ownerids:
        snd.senderr('you are not my owner lol')
        snd.exitcode(1)
        return
    
    if not args:
        snd.senderr('bad usage')
        snd.exitcode(1)
        return
    
    code = args[0].splitlines()
    code = list(map(lambda line: ' ' + line, code))
    code = '\n'.join(code)
    
    new_code = f'''async def run():\n{code}'''
    
    loc = {}
    try:
        exec(new_code, locals(), loc) # this creates run
        ret = await loc['run']()
    except Exception as err:
        tb = traceback.format_exc()
        snd.senderr(tb)
    else:
        if ret is not None:
            snd.sendout(str(ret))

