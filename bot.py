#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import debugger

from discord.ext import commands
import discord
import config

from cmd import cmd
from eval import Eval

prefix = config.prefix
token = config.token
cmds = config.cmds

intents = discord.Intents(messages=True, guilds=True, members=True, reactions=True)

bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command("help")

evaluator = Eval()

for c in cmds:
    debugger.__import__(c)

@bot.event
async def on_ready():
    print(f"{bot.user} is online")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.author == bot.user:
        return
    
    if message.content.startswith(prefix):
        #message.content = message.content.removeprefix(prefix)
        message.content = message.content[3:]
    
        ctx = await bot.get_context(message)
        await evaluator.basic_evaluator(ctx)
        

bot.run(token)
