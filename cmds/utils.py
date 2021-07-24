# -*- coding: utf-8 -*-
import discord
import aiohttp
from urllib.parse import urlparse

import json, toml
from pprint import pformat

from cmd import cmd
from aliases import command_aliases as aliases
import argutils; from argutils import ArgParse
import miscutils


trusted_netlocs = {'media.discordapp.net', 'images-ext-2.discordapp.net'}


class Utils:
    """Powerful util tool"""
    
    @cmd.new()
    @ArgParse.wrap(
        ArgParse()
            .add_argument(names=['t', 'title'])
            .add_argument(names=['d', 'description'])
            .add_argument(names=['u', 'url'])
            .add_argument(names=['n', 'thumbnail-url'])
            .add_argument(names=['a', 'author-name'])
            .add_argument(names=['r', 'author-url'])
            .add_argument(names=['l', 'author-icon'])
            .add_argument(names=['i', 'image-url'])
            .add_argument(names=['o', 'icon-url'])
            .add_argument(names=['f', 'footer'])
            .add_argument(names=['c', 'color'])
            
            .add_argument(names=['D', 'to-dict'], greedy=False)
            
            .test('-tdf lol'.split())
    )
    async def embed(snd, ctx, piped, args):
        '''
        whatis: generates an embed based on the given data
        man:
            usage: '{name} [data: string] {{options}}'
            prop:
                - PIPED [text|dict]
            description: >
                Generates an embed using the given data.
                If the piped data is a dict then the embed is generated based on that,
                otherwise, the data will be set as embed's description.
            examples:
                - |
                    embed -d 'hello world'
                - |
                    echo -t 'hello world' | embed
                - | 
                    json '{{"title": "Hello!","description": "Hi! :grinning:"}}' | embed
            
        '''
        
        if piped:
            if piped._stuff and type(piped._stuff) == dict:
                try:
                    embed = discord.Embed.from_dict(piped._stuff[0])
                    await ctx.send(embed=embed)
                except Exception:
                    snd.senderr("bad embed json")
                    snd.exitcode(1)
            elif piped._out:
                embed = discord.Embed(description=piped._out[0].decode('unicode_escape'))
                await ctx.send(embed=embed)
                
            return
        
            
        kwargs, args = args.parse()
        
        try:
            color = int(kwargs.color or '000000', 16)
            if color > 16777215:
                snd.senderr("color value should be less than or equal to FFFFFF")
                snd.exitcode(1)
                return 
        except ValueError:
            snd.senderr("invalid color code")
            snd.exitcode(1)
            return
        
        title = kwargs.title or ''
        description = kwargs.description or ''
        url = kwargs.url or ''
        
        footer = kwargs.footer or ''
        icon_url = kwargs.icon_url or ''
        
        author_name = kwargs.author_name or ''
        author_url = kwargs.author_url or ''
        author_icon = kwargs.author_icon or ''
        
        image_url = kwargs.image_url or ''
        
        thumbnail_url = kwargs.thumbnail_url or ''
        
        embed = (
            discord.Embed(title=title, description=description, url=url, color=color)
                .set_author(name=author_name, url=author_url, icon_url=author_icon)
                .set_thumbnail(url=thumbnail_url)
        )
        
        #$ title description url color
        
        for name, value in zip(args[::2], args[1::2]):
            embed.add_field(name=name, value=value)
            
        if 'to_dict' in kwargs:
            embed_dict =  embed.to_dict()
            snd.sendstuff(embed_dict)
            snd.sendout(str(embed_dict))
        else:
            try:
                await ctx.send(embed=embed)
            except Exception as err:
                snd.senderr(str(err))
                snd.exitcode(1)
        
        
    @cmd.new()
    @ArgParse.wrap(
        ArgParse()
            .add_argument(names=['l', 'list'], greedy=False)
            .add_argument(
                names=['f', 'format'],
                greedy=True
            )
            
            .test(["--list"])
    )
    async def file(snd, ctx, piped, args):
        kwargs, args = args.parse()
        attchs = ctx.message.attachments
        fmt_string = kwargs.format or 'id=$ID filename=$FILENAME size=$SIZE url=$URL type=$TYPE spoiler=$SPOILER\n'
        
        
        if 'list' in kwargs:
            for a in attchs:
                s = miscutils.fmt(fmt_string, '$', ID=a.id, FILENAME=a.filename, SIZE=a.size, URL=a.url, TYPE=a.content_type, SPOILER=a.is_spoiler())
                snd.sendout(s, end=b'')
        
        elif args:
            n = args[0]
            if not n.isdigit():
                snd.senderr('the argument must be an integer which must be greater than or equal to 1')
                snd.exitcode(1)
                return
            
            n = int(n)
        
            if n > len(attchs) or n < 1:
                snd.senderr('bad number')
                snd.exitcode(1)
                return
            
            attch = attchs[n - 1]
            
            if attch.size > 1000000:
                snd.senderr('file size must be less than 1MB')
                snd.exitcode(1)
                return
            
            content = await attch.read()
            
            snd.sendout(content, end=b'')
            
            
            
    @cmd.new()
    @ArgParse.wrap(
        ArgParse()
            #.add_argument(names=[''])
    )
    async def fetch(snd, ctx, piped, args):
        kwargs, args = args.parse()
        
        if not args:
            snd.senderr('bad usage')
            snd.exitcode(1)
            return 
        
        url = args[0]
        result = urlparse(url)
        
        if not all([result.scheme, result.netloc, result.path]):
            snd.senderr('bad url')
            snd.exitcode(1)
            return 
        
        if result.netloc not in trusted_netlocs:
            snd.senderr('untrusted url')
            snd.exitcode(1)
            return 
        
        
        try:
            async with aiohttp.request('GET', url=url) as response:
                #$ response
                headers = response.headers
                if 'Content-Length' not in headers:
                    snd.senderr('the url headers must specify the proper headers')
                    snd.exitcode(1)
                    return 
                
                if int(headers['Content-Length']) > 128000:
                    snd.senderr('content size must be less than or equal to 128KB')
                    snd.exitcode(1)
                    return
                
                content = await response.content.read()
                
                #$ content
                
        except Exception as err:
            raise err
        
        snd.sendout(content)
            
        

    @cmd.new()
    async def style(snd, ctx, piped, args):
        if len(args) >= 1:
            styles = {'bold': '**', 'italic': '_', 'underline': '__', 'strike': '~~', 'spoiler': '||', 'mark': '`'}
            style, *args = args
            if style in styles:
                style = styles[style]
                if piped and piped._out:
                    snd.sendout(style.encode() + b''.join(piped._out) + style.encode())
                else:
                    for arg in args:
                        snd.sendout(style + arg + style)
            else:
                snd.exitcode(1)
                snd.senderr("invaild style")
        else:
            snd.exitcode(1)
            snd.senderr("needs more than one arguments")
            
    @cmd.new()
    async def echo(snd, ctx, piped, args):
        if piped and piped._out:
            snd.sendout(b''.join(piped._out))
        else:
            snd.sendout(''.join(args))
            
    @cmd.new()
    async def printf(snd, ctx, piped, args):
        if piped and piped._out:
            snd.sendout(b''.join(piped._out), end=b'')
        else:
            snd.sendout(''.join(args), end=b'')
        
    @cmd.new()
    async def fmt(snd, ctx, piped, args):
        if piped and piped._out:
            for out in piped._out:
                snd.sendout(pformat(out.decode('unicode_escape')))
        else:
            snd.sendout(pformat(''.join(args)))
            
    @cmd.new()
    async def tr(snd, ctx, piped, args):
        if len(args) != 2:
            snd.senderr('needs exactly two arguments')
            return
        
        if piped and piped._out:
            snd.sendout(b''.join(piped._out).replace(*[arg.encode() for arg in args]))
        else:
            snd.sendout('direct usage is unimplemented. try piping')
          
    @cmd.new()
    async def toml(snd, ctx, piped, args):
        if piped and piped._stuff:
            if type(piped._stuff[0]) == dict:
                snd.sendout(toml.dumps(piped._stuff[0]))
            else:
                snd.exitcode(1)
                snd.senderr("not a dict")
            
    @cmd.new()
    async def json(snd, ctx, piped, args):
        if piped and piped._out:
            try:
                snd.sendstuff(json.loads(piped._out[0]))
            except Exception as err:
                snd.senderr(str(err))
                snd.exitcode(1)
        elif args:
            try:
                snd.sendout(json.loads(args[0]))
            except Exception as err:
                snd.senderr(str(err))
                snd.exitcode(1)
                
    @cmd.new()
    async def dbg(snd, ctx, piped, args):
        await ctx.send([piped._out, piped._err, piped._stuff, args])
        
    @cmd.new()
    async def alias(snd, ctx, piped, args):
        if len(args) == 1:
            
            nv = args[0].split('=')
            if len(nv) == 2:
                aliases[nv[0]] = nv[1].split()
                await ctx.send('alias set')
                print(aliases)
            else:
                snd.exitcode(1)
                snd.senderr("syntax error")
        elif len(args) == 0:
            snd.sendout(aliases)
        else:
            snd.exitcode(1)
            snd.senderr("needs exactly one argument")
        
    @cmd.new()
    async def cb(snd, ctx, piped, args):
        '''
        whatis: 'wraps given thing within a codeblock.'
        man:
            name: {name}
            usage: '[lang] [texts...]'
            prop: 
                - GREEDY
                - PIPED [texts...]
            description: |
                wraps given thing within a codeblock.
            examples:
                - |
                    {name} py 'print(69)'
                - |
                    echo 'puts 420' | {name} rb
        '''
        
        if len(args) >= 1:
            if piped and piped._out:
                snd.sendout(f'```{args[0]}\n'.encode() + b''.join(piped._out) + b'\n```')
            else:
                for arg in args:
                    snd.sendout(f'```{args[0]}\n' + arg + '\n```')
        else:
            snd.exitcode(1)
            snd.senderr("invaild usage")
            
            
    @cmd.new()
    async def pag():
        pass
