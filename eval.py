# -*- coding: utf-8 -*-

import discord
from cmd import cmd, Snd
from io import BytesIO
from aliases import command_aliases as aliases
from miscutils import pointer
import cmdutils

import config
PL = len(config.prefix)
PAD = " "

if config.speedups:
    try:
        import speedups

        tokenize = speedups.cmdutils.tokenize
        
        _cmdutils = speedups.cmdutils
        EscapeSeqEOFError = _cmdutils.EscapeSeqEOFError
        PatScanEOFError = _cmdutils.PatScanEOFError
        PatZeroLengthError = _cmdutils.PatZeroLengthError
        StringScanEOFError = _cmdutils.StringScanEOFError
        
    except ImportError:
        raise ImportError("cmdparser not found")
    else:
        print("optimizations are applied!")
else:
    #print("optimizations are disabled!")
    #from cmdutils import tokenize
    raise Exception("Optimizations cannot be disabled anymore!")

class Eval:
    """Command Evaluator"""

    async def basic_evaluator(self, ctx):
        content = msg = ctx.message.content

        try:
            tokens = tokenize(content)
            tree = cmdutils.tree(tokens)
            instrs, counts = cmdutils.parse(tree)
            print(tree)
        except IndexError:
            return await ctx.send("That's not a valid syntax/logic bruh.")
        except AssertionError:
            return await ctx.send("Didn't understand what you mean by that..")

            
        except PatScanEOFError as err:
            n, = err.args           
            return await ctx.send(
            pointer(msg=msg, pad=PAD, position=n, pl=PL, extra="\n") + 
                "End of message while scanning for the delimiter pair. "
                "Please check if your \* syntax is correct."
            )

        except EscapeSeqEOFError as err:
            n, = err.args
            return await ctx.send(
                pointer(msg=msg, pad=PAD, position=n, pl=PL, extra="\n") + 
                "That \\ at the end of your message is redundant. "
                "Remove it because I really despise it!"
                
            )

        except PatZeroLengthError as err:
            n, = err.args
            return await ctx.send(
                pointer(msg=msg, pad=PAD, position=n, pl=PL, extra="\n") + 
                "That's not how \\* syntax work! "
                "Perhaps remove the space after \\*."
            )

        except StringScanEOFError as err:
            n, = err.args
            return await ctx.send(
                pointer(msg=msg, pad=PAD, position=n, pl=PL, extra="\n") + 
                "You forgot to wrap your strings properly."
            )
                    

        (colncount, pipecount, filecount) = counts

        if pipecount > 7:
            return await ctx.send("Pipe limit exceeded.")
        if colncount > 3:
            return await ctx.send("Statement limit exceeded.")
        if filecount > 3:
            return await ctx.send("File limit exceeded.")

        piped = None
        outs = []
        errs = []
        files = {}
        for instr in instrs:
            inst, *left = instr
            print(f"{inst=}, {left=}")

            if inst in (cmdutils.EVAL, cmdutils.PIPE):
                left = left[0]

                if left[0] in aliases:
                    # print("yes")
                    left = aliases[left[0]] + left[1:]
                    # print(f'{left=}')

                cmdname, *args = left
                # print(f"{cmdname=}, {args=}")

                if not cmd.has(cmdname):
                    return await ctx.send(f"command `{cmdname}` not found.")

                try:
                    piped = await cmd.get(cmdname)(
                        ctx, (piped if inst == cmdutils.PIPE else None), args
                    )
                except Exception as err:
                    raise err

            elif inst == cmdutils.FILE:
                filename = left[0]
                if filename not in files:
                    files[filename] = []
                files[filename].append(
                    b"".join(piped._out) + b"".join(piped._err) if piped else b""
                )

                piped = None

            elif inst == cmdutils.FILEOUT:
                filename = left[0]
                if filename not in files:
                    files[filename] = []
                files[filename].append(b"".join(piped._out) if piped else b"")

                piped = Snd(err=piped._err)

            elif inst == cmdutils.FILEERR:
                filename = left[0]
                if filename not in files:
                    files[filename] = []
                files[filename].append(b"".join(piped._err) if piped else b"")

                piped = Snd(out=piped._out)

            elif inst == cmdutils.COLN:
                if piped:
                    outs.append(piped._out)
                    errs.append(piped._err)

                piped = None

            # if piped and (piped._exitcode not in (0, 1)):
            #    return await ctx.send(
            #        f'command `{cmdname}` exited with code {piped._exitcode}.' +
            #        (' Err: ' + b''.join(piped._err).decode('utf-8', 'replace')[:1800])
            #   )

        # now send it all
        content = (
            b"".join(
                b"".join((b"".join(out), b"".join(err))) for out, err in zip(outs, errs)
            )
            .decode("utf-8", "replace")
            .strip()[:1999]
            or "** **"
        )
        files = [
            discord.File(filename=filename, fp=BytesIO(b"".join(filebytes)))
            for filename, filebytes in files.items()
        ]

        await ctx.send(content=content, files=files)
