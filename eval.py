# -*- coding: utf-8 -*-

import discord
from cmd import cmd, Snd
from io import BytesIO
from aliases import command_aliases as aliases

import cmdutils

import config

if config.speedups:
    try:
        import speedups

        tokenize = speedups.cmdutils.tokenize
    except ImportError:
        raise ImportError("cmdparser not found")
    else:
        print("optimizations are applied!")
else:
    print("optimizations are disabled!")
    from cmdutils import tokenize


class Eval:
    """Command Evaluator"""

    async def basic_evaluator(self, ctx):
        content = ctx.message.content

        try:
            tokens = tokenize(content)
            tree = cmdutils.tree(tokens)
            instrs, counts = cmdutils.parse(tree)
            print(tree)
        except IndexError:
            return await ctx.send("syntax error.")
        except AssertionError:
            return await ctx.send("syntax error.")
        except Exception as err:
            return await ctx.send("syntax error.")
            print(str(err), err)

        (colncount, pipecount, filecount) = counts

        if pipecount > 7:
            return await ctx.send("pipe limit exceeded.")
        if colncount > 3:
            return await ctx.send("statement limit exceeded.")
        if filecount > 3:
            return await ctx.send("file limit exceeded.")

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
