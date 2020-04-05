import os, sys
import json
import discord
from Commands.Pingpong import *
from itertools import cycle
from discord.ext import commands, tasks
import ntplib
from datetime import datetime, timezone

with open('data\\key.k', 'r') as f:
    TokenData = json.load(f)

BotToken = TokenData['COVID-19']

Bot_Version = 'Beta 0.0.1'
print("Starting up...")
defaultPrefixes = '>'
defaultLang = 'en' # Support en and kr
totalCases, totalDeaths, totalRecovered

if os.path.exists('data\\prefixes.data') is False:
    with open('data\\prefixes.data', 'w') as f:
        f.write('{}')
    f.close

if os.path.exists('data\\lang.data') is False:
    with open('data\\lang.data', 'w') as f:
        f.write('{}')
    f.close

def getPrefix(client, message): # Return the prefix for the server.
    if ifDM:
        return defaultPrefixes

    with open('data\\prefixes.data', 'r') as f:
        prefixes = json.load(f)

    try:
        prefix = prefixes[str(message.guild.id)]
    except: # If the server is never registered, set the prefixes for the server.
        prefix = defaultPrefixes # Default prefixes
        prefixes[str(message.guild.id)] = prefix
        with open('data\\prefixes.data', 'w') as f:
            json.dump(prefixes, f, indent = 4)

    return prefix

def getLang(client, message): # Return the language for the server.
    if ifDM:
        return defaultLang

    with open('data\\lang.data', 'r') as f:
        lang = json.load(f)

    try:
        lang = languages[str(message.guild.id)]
    except: # If the server is never registered, set the language for the server.
        lang = defaultLang # Default language
        languages[str(message.guild.id)] = lang
        with open('data\\lang.data', 'w') as f:
            json.dump(languages, f, indent = 4)
            
    return lang

client = commands.Bot(command_prefix = getPrefix, case_insensitive = True) # Ignore the upper/lower case
status = cycle(["'>도움' 명령어로 도움말을 받으실 수 있습니다.", "Say >help", f"Total Cases: {totalCases}", f"Total Deaths: {totalDeaths}", f"Total Recovered: {totalRecovered}"]) # Status message array

@client.event
async def on_ready():
    print('-' * 30)
    print('[Login info]')
    print(f'Bot Name: {client.user.name}')
    print(f'Bot ID: {client.user.id}')
    print(f'Bot Verson: {Bot_Version}')
    print('-' * 30)
    change_status.start() # Start the cycling status message.

@tasks.loop(seconds = 15)
async def change_status(): # Change the Bot's status message for every 15 seconds.
    activity = discord.Activity(name = next(status), type = discord.ActivityType.listening)
    await client.change_presence(activity = activity)

@client.event
async def on_guild_join(guild): # Register the new server prefix and language.
    with open('data\\prefixes.data', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = defaultPrefixes
    
    with open('data\\prefixes.data', 'w') as f:
        json.dump(prefixes, f, indent = 4)


    with open('data\\lang.data', 'r') as f:
        languages = json.load(f)

    languages[str(guild.id)] = defaultLang
    
    with open('data\\lang.data', 'w') as f:
        json.dump(languages, f, indent = 4)

@client.event
async def on_guild_remove(guild): # Remove the server prefixes and language.
    with open('data\\prefixes.data', 'r') as f:
        prefixes = json.load(f)
        
    prefixes.pop(str(guild.id))
    
    with open('data\\prefixes.data', 'w') as f:
        json.dump(prefixes, f, indent = 4)


    with open('data\\lang.data', 'r') as f:
        languages = json.load(f)

    languages.pop(str(guild.id))
    
    with open('data\\lang.data', 'w') as f:
        json.dump(languages, f, indent = 4)

def ifDM(ctx): # Check if it is DM.
    return ctx.guild is False

@client.event
async def on_message(message): # On Message Event: this will be executed every single time when someone sends the message.
    if message.author.bot: # Ignore the self's message.
        return None
    elif message.content.startswith(getPrefix(client, message)):
        log(message)
    await client.process_commands(message)

def log(message):
    print(f'[{message.author.name}:{message.author.id}] {message.content}')

@client.command()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def setPrefix(ctx, prefix): # Change the prefix.
    if ifDM:
        await ctx.send("You are not able to change the prefix when you're messaging via DM. \nUse '>' as a prefix.")
        return None

    with open('data\\prefixes.data', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix
    
    with open('data\\prefixes.data', 'w') as f:
        json.dump(prefixes, f, indent = 4)
    await ctx.send(f"Server prefix has been successfully changed to {prefix}.")

@client.command()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def setLang(ctx, lang): # Change the prefix.
    if ifDM:
        await ctx.send("You are not able to change the language when you're messaging via DM. \nHowever, you still able to use the bot's function with a default language, English.")
        return None

    with open('data\\lang.data', 'r') as f:
        languages = json.load(f)

    languages[str(ctx.guild.id)] = lang
    
    with open('data\\lang.data', 'w') as f:
        json.dump(languages, f, indent = 4)
    await ctx.send(f"Server language has been successfully changed to {lang}.")

@tasks.loop(seconds = 15)
async def change_status(): # Change the Bot's status message for every 15 seconds.
    activity = discord.Activity(name = next(status), type = discord.ActivityType.listening)
    await client.change_presence(activity = activity)
 
async def getData(ctx, lang): # Get current time in UTC.
    c = ntplib.NTPClient()
    # NTP server ip
    response = c.request('time.google.com', version=3)
    response.offset 
    # Get time based on UTC timezone.
    return datetime.fromtimestamp(response.tx_time, timezone.utc)

client.run(BotToken)