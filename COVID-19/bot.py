import os, sys
import json
import urllib
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

if os.path.exists('data/ServerData.json') is False:
    with open('data/ServerData.json', 'w') as f:
        f.write('{}')

def ifDM(ctx): # Check if it is DM.
    if (ctx.guild == None):
        return 'DM'
    else:
        return 'Server'

def getDefault(dataType):
    return {
        'prefix':'>',
        'language':'en',
        'notification':True
    }.get(dataType, False)

def getData(client, message, dataType='prefix'):
    # dataType: prefix, language, notification
    defaultValue = getDefault(dataType)
    chatType = ifDM(message)

    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)

    try:
        data = serverData[chatType][str(message.guild.id)][dataType]
    except: # If the server is never registered, set the default data for the server.
        data = defaultValue # Default data
        serverData[chatType][str(message.guild.id)][dataType] = data
        with open('data/ServerData.json', 'w') as f:
            json.dump(serverData, f, indent = 4)
    return data

client = commands.Bot(command_prefix = getData, case_insensitive = True) # Ignore the upper/lower case
status = cycle(['\'>도움\' 명령어로 도움말을 받으실 수 있습니다.', 'Say >help'])

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
    global status # Status message array
    activity = discord.Activity(name = next(status), type = discord.ActivityType.watching)
    await client.change_presence(activity = activity)

@client.event
async def on_message(message): # On Message Event: this will be executed every single time when someone sends the message.
    if message.author.bot: # Ignore the self's message.
        return None
    elif message.content.startswith(getData()):
        log(message)
    await client.process_commands(message)

def log(message):
    print(f'[{message.author.name}:{message.author.id}] {message.content}')

@client.event
async def on_guild_join(guild): # Register the new server prefix and language.
    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)
    serverData['Server'][str(guild.id)]['prefix'] = getDefault('prefix')
    serverData['Server'][str(guild.id)]['language'] = getDefault('language')
    serverData['Server'][str(guild.id)]['notification'] = getDefault('notification')
    
    with open('data/ServerData.json', 'w') as f:
        json.dump(serverData, f, indent = 4)

@client.event
async def on_guild_remove(guild): # Remove the server prefixes and language.
    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)
    serverData['Server'].pop(str(guild.id))
    
    with open('data/ServerData.json', 'w') as f:
        json.dump(serverData, f, indent = 4)

@client.command()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def setPrefix(ctx, prefix): # Change the prefix.
    chatType = ifDM(ctx)
    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)
    serverData[chatType][str(ctx.guild.id)]['prefix'] = prefix
    
    with open('data/ServerData.json', 'w') as f:
        json.dump(serverData, f, indent = 4)
    await ctx.send(f'Server prefix has been successfully changed to {prefix}.')

@client.command()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def setLanguage(ctx, language): # Change the prefix.
    chatType = ifDM(ctx)
    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)
    serverData[chatType][str(ctx.guild.id)]['language'] = language
    
    with open('data/ServerData.json', 'w') as f:
        json.dump(serverData, f, indent = 4)
    await ctx.send(f'Server language has been successfully changed to {language}.')

@client.command()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def setNotification(ctx, notification): # Change the prefix.
    chatType = ifDM(ctx)
    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)
    serverData[chatType][str(ctx.guild.id)]['notification'] = notification
    
    with open('data/ServerData.json', 'w') as f:
        json.dump(serverData, f, indent = 4)
    await ctx.send(f'Server notification setting has been successfully changed to {notification}.')

predictionJson = None
dataJson = None
lastUpdated = 'never'
def getData():
    print('[System] Updating the data...')
    global dataJson
    global lastUpdated
    URL = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Actions/master/LastUpdated/data.json'
    urllib.request.urlretrieve(URL, 'data/DailyReports/data.json')
    with open('data/DailyReports/data.json', 'r') as f:
        dataJson = json.load(f)

    if (lastUpdated != dataJson['last_updated']):
        global predictionJson
        global status
        URL = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Actions/master/LastUpdated/prediction.json'
        urllib.request.urlretrieve(URL, 'data/DailyReports/prediction.json')
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

        a = f"Confirmed: {dataJson['total_confirmed']}"
        b = f"Deaths: {dataJson['total_deaths']}"
        c = f"Recovered: {dataJson['total_recovered']}"
        d = f"Mortality %: {round(dataJson['mortality_rate'] * 100, 2)}"
        e = f"Recovery %: {round(dataJson['recovery_rate'] * 100, 2)}"
        status = cycle(['\'>도움\' 명령어로 도움말을 받으실 수 있습니다.', 'Say >help', a, b, c, d, e])

        if (lastUpdated != 'never'):
            # Send out data update notification to all server.
            print('Data update notification were sented.')

        lastUpdated = dataJson['last_updated']
    print('[System] Update finished.')

def autoUpdate():
    timer = threading.Timer(3600, autoUpdate)
    print('[System] Scheduled update starting...')
    print(f'Time: {datetime.datetime.now()}')
    getData()
    timer.start()

@client.command()
async def covid(ctx):
    global dataJson
    Confirmed = dataJson['total_confirmed']
    Deaths = dataJson['total_deaths']
    Recovered = dataJson['total_recovered']
    targetTime = dataJson['last_updated']
    Embed = discord.Embed(
        title = f'Global Cases ({targetTime})',
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