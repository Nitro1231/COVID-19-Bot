import os, sys
import json
import discord
import datetime
import threading
from itertools import cycle
from discord.ext import commands, tasks

with open('data/key.k', 'r') as f:
    TokenData = json.load(f)

BotToken = TokenData['COVID-19']

Bot_Version = 'Beta 0.0.1'
print('Starting up...')
defaultPrefixes = '>'
defaultLang = 'en' # Support en and kr
notification = True

if os.path.exists('data/data.data') is False:
    with open('data/data.data', 'w') as f:
        f.write('{}')

def ifDM(ctx): # Check if it is DM.
    return ctx.guild == None

def getPrefix(client, message): # Return the prefix for the server.
    if ifDM(message):
        return defaultPrefixes

    with open('data/prefixes.data', 'r') as f:
        prefixes = json.load(f)

    try:
        prefix = prefixes[str(message.guild.id)]
    except: # If the server is never registered, set the prefixes for the server.
        prefix = defaultPrefixes # Default prefixes
        prefixes[str(message.guild.id)] = prefix
        with open('data/prefixes.data', 'w') as f:
            json.dump(prefixes, f, indent = 4)
    return prefix

def getLang(client, message): # Return the language for the server.
    if ifDM(message):
        return defaultLang

    with open('data/lang.data', 'r') as f:
        lang = json.load(f)

    try:
        lang = languages[str(message.guild.id)]
    except: # If the server is never registered, set the language for the server.
        lang = defaultLang # Default language
        languages[str(message.guild.id)] = lang
        with open('data/lang.data', 'w') as f:
            json.dump(languages, f, indent = 4)
    return lang

client = commands.Bot(command_prefix = getPrefix, case_insensitive = True) # Ignore the upper/lower case

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
    status = cycle(['\'>도움\' 명령어로 도움말을 받으실 수 있습니다.', 'Say >help']) # Status message array
    activity = discord.Activity(name = next(status), type = discord.ActivityType.watching)
    await client.change_presence(activity = activity)

@client.event
async def on_message(message): # On Message Event: this will be executed every single time when someone sends the message.
    if message.author.bot: # Ignore the self's message.
        return None
    elif message.content.startswith(getPrefix(client, message)):
        log(message)
    await client.process_commands(message)

def log(message):
    print(f'[{message.author.name}:{message.author.id}] {message.content}')

@client.event
async def on_guild_join(guild): # Register the new server prefix and language.
    with open('data/prefixes.data', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = defaultPrefixes
    
    with open('data/prefixes.data', 'w') as f:
        json.dump(prefixes, f, indent = 4)


    with open('data/lang.data', 'r') as f:
        languages = json.load(f)
    languages[str(guild.id)] = defaultLang
    
    with open('data/lang.data', 'w') as f:
        json.dump(languages, f, indent = 4)

@client.event
async def on_guild_remove(guild): # Remove the server prefixes and language.
    with open('data/prefixes.data', 'r') as f:
        prefixes = json.load(f)
    prefixes.pop(str(guild.id))
    
    with open('data/prefixes.data', 'w') as f:
        json.dump(prefixes, f, indent = 4)


    with open('data/lang.data', 'r') as f:
        languages = json.load(f)
    languages.pop(str(guild.id))
    
    with open('data/lang.data', 'w') as f:
        json.dump(languages, f, indent = 4)

@client.command()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def setPrefix(ctx, prefix): # Change the prefix.
    if ifDM(ctx):
        await ctx.send('You are not able to change the prefix when you\'re messaging via DM. \nUse \'>\' as a prefix.')
        return None

    with open('data/prefixes.data', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix
    
    with open('data/prefixes.data', 'w') as f:
        json.dump(prefixes, f, indent = 4)
    await ctx.send(f'Server prefix has been successfully changed to {prefix}.')

@client.command()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def setLang(ctx, lang): # Change the prefix.
    if ifDM(ctx):
        await ctx.send('You are not able to change the language when you\'re messaging via DM. \nHowever, you still able to use the bot\'s function with a default language, English.')
        return None

    with open('data/lang.data', 'r') as f:
        languages = json.load(f)
    languages[str(ctx.guild.id)] = lang
    
    with open('data/lang.data', 'w') as f:
        json.dump(languages, f, indent = 4)
    await ctx.send(f'Server language has been successfully changed to {lang}.')

predictionJson = ''
dataJson = ''
lastUpdated = 'never'
def getData():
    print('[System] Updating the data...')
    global predictionJson
    global dataJson
    URL = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Actions/master/LastUpdated/prediction.json'
    urllib.request.urlretrieve(URL, 'data/DailyReports/prediction.json')
    URL = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Actions/master/LastUpdated/data.json'
    urllib.request.urlretrieve(URL, 'data/DailyReports/data.json')
    URL = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Actions/master/LastUpdated/Reorganized/combined.csv'
    urllib.request.urlretrieve(URL, 'data/DailyReports/combined.csv')
    URL = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Actions/master/LastUpdated/Reorganized/confirmed.csv'
    urllib.request.urlretrieve(URL, 'data/DailyReports/confirmed.csv')
    URL = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Actions/master/LastUpdated/Reorganized/deaths.csv'
    urllib.request.urlretrieve(URL, 'data/DailyReports/deaths.csv')
    URL = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Actions/master/LastUpdated/Reorganized/recovered.csv'
    urllib.request.urlretrieve(URL, 'data/DailyReports/recovered.csv')

    with open('data/DailyReports/prediction.json', 'r') as f:
        predictionJson = json.load(f)
    with open('data/DailyReports/data.json', 'r') as f:
        dataJson = json.load(f)

    print('[System] Update finished.')

def autoUpdate():
    timer = threading.Timer(3600, autoUpdate)
    print('[System] Scheduled update starting...')
    print(f'Time: {datetime.datetime.now()}')
    getData()
    timer.start()

@client.command()
async def covid(ctx):
    Confirmed = 1
    Deaths = 1
    Recovered = 1
    targetTime = 'test'
    Embed = discord.Embed(
        title = f'Global Cases ({targetTime} UTC)',
        colour = discord.Colour.red()
    )
    Embed.set_author(name = f'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    #Embed.set_thumbnail(url = User_Json['profile_image_url'])
    Embed.add_field(name = '<:Confirmed:699600701134733333> Confirmed', value = f'**{Confirmed}**', inline = True)
    Embed.add_field(name = '<:Deaths:699600701017292860> Deaths', value = f'**{Deaths}**', inline = True)
    Embed.add_field(name = '<:Recovered:699600700753051668> Recovered', value = f'**{Recovered}**', inline = True)
    Embed.add_field(name = '<:Active:699611837670490242> Active', value = f'**{Confirmed - Recovered - Deaths}**', inline = True)
    Embed.add_field(name = '<:Mortality_Rate:699600701227139122> Mortality Rate', value = f'**{round(Deaths / Confirmed * 100, 2)}%**', inline = True)
    Embed.add_field(name = '<:Recovery_Rate:699600700707176468> Recovery Rate', value = f'**{round(Recovered / Confirmed * 100, 2)}%**', inline = True)
    Embed.set_image(url='https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/COVID-19_Outbreak_World_Map_per_Capita.svg/800px-COVID-19_Outbreak_World_Map_per_Capita.svg.png')
    Embed.set_footer(text = f'Data from Johns Hopkins, Last Update at {targetTime}', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png')
    await ctx.send(embed = Embed)

@client.command()
async def top10(ctx):
    await ctx.send(file=discord.File(finalPic))

autoUpdate()
client.run(BotToken)