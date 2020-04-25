import os, sys
import json
import time
import urllib
import asyncio
import discord
import threading
from itertools import cycle
from datetime import datetime
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType

with open('data/key.k', 'r') as f:
    TokenData = json.load(f)

DevelopmentVer = True

if DevelopmentVer:
    BotToken = TokenData['Dev']
else:
    BotToken = TokenData['COVID-19']

timeLimit = 30
coolDownTime = 10
coolDownLimit = 3
reply = 0
adminID = TokenData['Admin']
Bot_Version = 'Beta 0.0.2'
print('Starting up...')
startTime = datetime.now()

# region Server Properties
if os.path.exists('data/ServerData.json') is False:
    with open('data/ServerData.json', 'w') as f:
        f.write('{"DM":{}, "Server":{}}')

def getChatInfo(ctx): # Check if it is DM.
    if (ctx.guild == None):
        return 'DM', str(ctx.author.id)
    else:
        return 'Server', str(ctx.guild.id)

def getDefault(dataType):
    return {
        'prefix':'>',
        'language':'en',
        'notification':True
    }.get(dataType, False)

def setData(jsonData, chatType, chatID, dataType, defaultValue):
    if (chatID in jsonData[chatType]) == False:
        jsonData[chatType][chatID] = {}

    jsonData[chatType][chatID][dataType] = {}
    jsonData[chatType][chatID][dataType] = defaultValue
    with open('data/ServerData.json', 'w') as f:
        json.dump(jsonData, f, indent = 4)
    return defaultValue

def setMissingData(jsonData, chatType, chatID):
    if (chatID in jsonData[chatType]) == False:
        setData(jsonData, chatType, chatID, 'prefix', getDefault('prefix'))
        setData(jsonData, chatType, chatID, 'language', getDefault('language'))
        setData(jsonData, chatType, chatID, 'notification', getDefault('notification'))
    else:
        dataType = ['prefix', 'language', 'notification']
        for data in dataType:
            if (data in jsonData[chatType][chatID]) == False:
                setData(jsonData, chatType, chatID, data, getDefault(data))

    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)
    return serverData

def getData(client, message, dataType='prefix'):
    # dataType: prefix, language, notification
    defaultValue = getDefault(dataType)
    chatType, chatID = getChatInfo(message)

    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)

    serverData = setMissingData(serverData, chatType, chatID)

    try:
        data = serverData[chatType][chatID][dataType]
    except: # If the server is never registered, set the default data for the server.
        data = setData(serverData, chatType, chatID, dataType, getDefault(dataType))
        print('[Error] get data error, this should not be happend anyway...')
    return data

# endregion

# region Main Function
client = commands.Bot(command_prefix = getData, case_insensitive = True) # Ignore the upper/lower case
client.remove_command('help')
status = cycle(['\'>도움\' 명령어로 도움말을 받으실 수 있습니다.', 'Say >help'])
emoji = ['<:medicine:700748997215649832>', '<:favicon:699600700446867600>', '<:coronavirus:700748996846551161>', '<:analytics:701800964444651635>', '<:virus:700748997303861341>', '<:content:700748996821647523>']

@client.event
async def on_ready():
    client.AppInfo = await client.application_info()
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
    elif message.content.startswith(getData(client, message)):
        log(message)
    global reply
    reply += 1
    await client.process_commands(message)

def log(message):
    print(f'[{message.author.name}:{message.author.id}] {message.content}')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Cannot find command `{ctx.message.content}`.\nIf you don\'t know how to use this bot, try `{getData(client, ctx.message)}help`.')
    elif isinstance(error, commands.CommandOnCooldown):
        print(f'[Warning] Cooldown limitation was reached by {ctx.message.author.name}:{ctx.message.author.id} in Guild({ctx.message.guild}).')
        message = f'To prevent overtraffic of the server, you are not able to use more than {coolDownLimit} commands per {coolDownTime} seconds. Thank you for your understanding.'
        await ctx.send(message)
    else:
        print(f'[Error] An error has occurred while executing the command "{ctx.message.content}".\nError Info: {error}')
        message = f'An unknown error occurred while executing the command.\nIf this error keep occurred, please contact with developer.\nError information: ```{error}```'
        await ctx.send(message)

def adminCheck(ctx): # @commands.check(adminCheck)
    global adminID
    return (str)(ctx.author.id) == adminID
# endregion

# region Server Properties
@client.event
async def on_guild_join(guild): # Register the new server prefix and language.
    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)
    setData(serverData, 'Server', str(guild.id), 'prefix', getDefault('prefix'))
    setData(serverData, 'Server', str(guild.id), 'language', getDefault('language'))
    setData(serverData, 'Server', str(guild.id), 'notification', getDefault('notification'))

@client.event
async def on_guild_remove(guild): # Remove the server prefixes and language.
    with open('data/ServerData.json', 'r') as f:
        serverData = json.load(f)
    serverData['Server'].pop(str(guild.id))
    
    with open('data/ServerData.json', 'w') as f:
        json.dump(serverData, f, indent = 4)

def checkPermissions(ctx, chatType):
    if chatType == 'DM':
        return True
    pm = ctx.message.author.guild_permissions
    if (pm.manage_messages == True) or (pm.administrator == True) or (pm.manage_roles == True):
        return True
    return False

def changeServerSetting(ctx, dataType, data, description):
    chatType, chatID = getChatInfo(ctx)
    if checkPermissions(ctx, chatType):
        with open('data/ServerData.json', 'r') as f:
            serverData = json.load(f)
        setData(serverData, chatType, chatID, dataType, data)
        return ctx.send(f'Server {description} has been successfully changed to `{data}`.')
    else:
        return ctx.send(f'You do not have permission to change the server `{description}`.')

@client.command()
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def setPrefix(ctx, prefix=None): # Change the prefix.
    if prefix == None:
        return await ctx.send('You cannot use blank for the prefix.')
    return await changeServerSetting(ctx, 'prefix', prefix, '`prefix`')

@client.command()
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def setLanguage(ctx, language=None): # Change the prefix.
    if language == 'en' or language == 'kr':
        return await changeServerSetting(ctx, 'language', language, '`language`')
    else:
        return await ctx.send('Currently, only `en` (English) available. However, you also can change the language to `kr` (Korean), and it will automatically applied when it became available.')

@client.command()
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def setNotification(ctx, notification=None): # Change the prefix.
    if notification == 'True' or notification == 'true':
        return await changeServerSetting(ctx, 'notification', True, '`notification` setting')
    elif notification == 'False' or notification == 'false':
        return await changeServerSetting(ctx, 'notification', False, '`notification` setting')
    else:
        return await ctx.send('This command required only `True` or `False` as a perimeter.')

# endregion

# region Covid-19
predictionJson = None
dataJson = None
lastUpdated = 'never'
def updateData():
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
        d = f"Mortality: {round(dataJson['mortality_rate'] * 100, 2)}%"
        e = f"Recovery: {round(dataJson['recovery_rate'] * 100, 2)}%"
        status = cycle(['\'>도움\' 명령어로 도움말을 받으실 수 있습니다.', 'Say >help', a, b, c, d, e])

        if (lastUpdated != 'never'):
            # Send out data update notification to all server.
            print('Data update notification were sented.')

        lastUpdated = dataJson['last_updated']
    print('[System] Update finished.')

def autoUpdate():
    timer = threading.Timer(3600, autoUpdate)
    print('[System] Scheduled update starting...')
    print(f'Time: {datetime.now()}')
    updateData()
    timer.start()

# endregion

# region Command
@client.command(pass_context=True, aliases=['hp','도움','도움말'])
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def help(ctx):
    cType, __ = getChatInfo(ctx)
    channel = await ctx.message.author.create_dm()
    Embed = discord.Embed(
        title = 'Help',
        timestamp = ctx.message.created_at,
        colour = discord.Colour.red()
    )
    prefix = getData(client, ctx.message)
    Embed.set_author(name = 'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    Embed.add_field(name = f'**{prefix}help**', value = f'{emoji[0]}_You also can use ``hp``_\nShows the list of commands that you can use.', inline = False)
    Embed.add_field(name = f'**{prefix}covid**', value = f'{emoji[1]}_You also can use ``c``_\nProvide live data dashboard of COVID-19.', inline = False)
    Embed.add_field(name = f'**{prefix}top10**', value = f'{emoji[2]}_You also can use ``t10``_\nProvide a graph of Top-10 countries with most confirmed cases.', inline = False)
    Embed.add_field(name = f'**{prefix}prediction**', value = f'{emoji[3]}_You also can use ``pd``_\nProvide a prediction graph of COVID-19. Don\'t panic, it is just a prediction.', inline = False)
    Embed.add_field(name = f'**{prefix}coronavirus**', value = f'{emoji[4]}_You also can use ``cv``_\nProvide information about COVID-19 with some useful tips.', inline = False)
    Embed.add_field(name = f'**{prefix}coronalive**', value = f'{emoji[5]}_You also can use ``cl``_\nCheck out our live-dashboard website, CoronaLive!', inline = False)
    Embed.add_field(name = '-' * 20, value = '(ง˙∇˙)ว', inline = False)
    Embed.add_field(name = f'**{prefix}info**', value = f'_There is no replacement command..._\nProvide information about this bot.', inline = False)
    Embed.add_field(name = f'**{prefix}admin**', value = '_There is no replacement command..._\nAdmin command for those who own the server or using DM.', inline = False)
    Embed.add_field(name = f'**{prefix}ping**', value = '_There is no replacement command..._\nPong!', inline = False)
    Embed.add_field(name = f'**{prefix}shortcut**', value = '_You also can use ``sc``_\nEasy way to call other commands with an emoji reaction.', inline = False)
    Embed.add_field(name = '-' * 20, value = 'Extra Information', inline = False)
    Embed.add_field(name = '**Time out**', value = f'Every emoji reaction has {timeLimit} seconds time limit.\nAfter {timeLimit} seconds, your reaction will be ignored.', inline = False)
    Embed.set_footer(text = 'NitroStudio')
    if cType == 'Server':
        await channel.send(embed=Embed)
        await ctx.send(':incoming_envelope: Yo! I just sent what I can do for you via DM message. Check that out! :v:')
    else:
        await ctx.send(embed=Embed)

@client.command(aliases=['정보'])
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def info(ctx):
    global startTime
    global botInfo
    upTime = datetime.now() - startTime
    admin = client.AppInfo.owner

    users = 0
    for guild in client.guilds:
        users += len(guild.members)

    Embed = discord.Embed(
        title = 'Information',
        timestamp = ctx.message.created_at,
        colour = discord.Colour.red()
    )
    Embed.set_author(name = 'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    Embed.set_thumbnail(url=admin.avatar_url)
    Embed.add_field(name='**Developer**', value=admin, inline=False)
    Embed.add_field(name='**Uptime**', value=upTime, inline=False)
    Embed.add_field(name='**Users**', value=users, inline=True)
    Embed.add_field(name='**Server**', value=len(client.guilds), inline=True)
    Embed.add_field(name='**Responded**', value=reply, inline=False)
    Embed.add_field(name='**Bot Version**', value=Bot_Version, inline=False)
    Embed.add_field(name='**Discord.py Version**', value=discord.__version__, inline=False)
    Embed.set_footer(text = 'NitroStudio')
    await ctx.send(embed=Embed)

@client.command(aliases=['c'])
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def covid(ctx):
    global dataJson
    cType, __ = getChatInfo(ctx)
    emoji = ['<:linear:701313021607280670>', '<:logistics:701313021401890908>']
    Confirmed = dataJson['total_confirmed']
    Deaths = dataJson['total_deaths']
    Recovered = dataJson['total_recovered']
    targetTime = dataJson['last_updated']
    Embed = discord.Embed(
        title = f'Global Cases ({targetTime})',
        colour = discord.Colour.red()
    )
    Embed.set_author(name = f'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    Embed.add_field(name = '<:Confirmed:699600701134733333> Confirmed', value = f'**{Confirmed}**', inline = True)
    Embed.add_field(name = '<:Deaths:699600701017292860> Deaths', value = f'**{Deaths}**', inline = True)
    Embed.add_field(name = '<:Recovered:699600700753051668> Recovered', value = f'**{Recovered}**', inline = True)
    Embed.add_field(name = '<:Active:699611837670490242> Active', value = f'**{Confirmed - Recovered - Deaths}**', inline = True)
    Embed.add_field(name = '<:Mortality_Rate:699600701227139122> Mortality Rate', value = f'**{round(Deaths / Confirmed * 100, 2)}%**', inline = True)
    Embed.add_field(name = '<:Recovery_Rate:699600700707176468> Recovery Rate', value = f'**{round(Recovered / Confirmed * 100, 2)}%**', inline = True)
    Embed.set_image(url='https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/COVID-19_Outbreak_World_Map_per_Capita.svg/800px-COVID-19_Outbreak_World_Map_per_Capita.svg.png')
    Embed.set_footer(text = f'Data from Johns Hopkins, Last Update at {targetTime}', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png')
    msg = await ctx.send(embed = Embed)

    for e in emoji:
        await msg.add_reaction(e)

    def check(reaction, user):
        return (user == ctx.author) and (reaction.message.id == msg.id)
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=timeLimit, check=check)
        reaction = str(reaction)
    except asyncio.TimeoutError: # this will excute when the time is out.
        if cType != 'DM':
            await msg.clear_reactions()
    else:
        if reaction == emoji[0]:
            gEmbed = discord.Embed(
                title = f'Global Cases Linear Graph ({targetTime})',
                colour = discord.Colour.red()
            )
            gEmbed.set_author(name = f'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
            gEmbed.set_image(url= f'https://github.com/Nitro1231/COVID-19-Actions/blob/master/DailyReports/{dataJson["date"]}/Img/global_linear_t.png?raw=true')
            gEmbed.set_footer(text = f'Data from Johns Hopkins, Last Update at {targetTime}', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png')
            await ctx.send(embed = gEmbed)
        elif reaction == emoji[1]:
            gEmbed = discord.Embed(
                title = f'Global Cases Logistic Graph ({targetTime})',
                colour = discord.Colour.red()
            )
            gEmbed.set_author(name = f'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
            gEmbed.set_image(url= f'https://github.com/Nitro1231/COVID-19-Actions/blob/master/DailyReports/{dataJson["date"]}/Img/global_log_t.png?raw=true')
            gEmbed.set_footer(text = f'Data from Johns Hopkins, Last Update at {targetTime}', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png')
            await ctx.send(embed = gEmbed)
    if cType != 'DM':
        await msg.clear_reactions()

@client.command(aliases=['t10', '탑'])
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def top10(ctx):
    global dataJson
    Confirmed = dataJson['total_confirmed']
    Deaths = dataJson['total_deaths']
    Recovered = dataJson['total_recovered']
    targetTime = dataJson['last_updated']
    Embed = discord.Embed(
        title = f'TOP-10 Cases ({targetTime})',
        colour = discord.Colour.red()
    )
    Embed.set_author(name = f'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    Embed.set_image(url = f'https://github.com/Nitro1231/COVID-19-Actions/blob/master/DailyReports/{dataJson["date"]}/Img/top10_t.png?raw=true')
    Embed.set_footer(text = f'Data from Johns Hopkins, Last Update at {targetTime}', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png')
    return await ctx.send(embed = Embed)

@client.command(aliases=['pd', '예측'])
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def prediction(ctx):
    global predictionJson
    global dataJson
    total_confirmed_prediction = predictionJson['total_confirmed_prediction']
    total_confirmed_difference = predictionJson['total_confirmed_difference']
    tomorrow = predictionJson['tomorrow']
    tomorrow_confirmed_prediction = predictionJson['tomorrow_confirmed_prediction']
    tomorrow_confirmed_difference = predictionJson['tomorrow_confirmed_difference']
    total_days = predictionJson['total_days']
    days_remained = predictionJson['days_remained']
    final_day_prediction = predictionJson['final_day_prediction']
    targetTime = predictionJson['last_updated']
    Embed = discord.Embed(
        title = f'Global Prediction Cases ({targetTime})',
        colour = discord.Colour.red()
    )
    Embed.set_author(name = f'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    Embed.add_field(name = 'Total predicted cases', value = f'**{total_confirmed_prediction} (+ {total_confirmed_difference})**', inline = False)
    Embed.add_field(name = f'Predicted Cases for Tomorrow ({tomorrow})', value = f'**{tomorrow_confirmed_prediction} (+ {tomorrow_confirmed_difference})**', inline = False)
    Embed.add_field(name = 'Total days', value = f'**{total_days}** ({days_remained} days remain)', inline = False)
    Embed.add_field(name = 'Predicted final day', value = f'**{final_day_prediction}**', inline = False)
    Embed.add_field(name = '-' * 20, value = f'This is just a prediction. It is up to you to believe this or not.', inline = False)
    Embed.set_image(url = f'https://github.com/Nitro1231/COVID-19-Actions/blob/master/DailyReports/{dataJson["date"]}/Img/prediction_t.png?raw=true')
    Embed.set_footer(text = f'Data from Johns Hopkins, Last Update at {targetTime}', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png')
    await ctx.send(embed = Embed)

@client.command(aliases=['cv', '코로나바이러스', '코로나'])
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def coronavirus(ctx):
    Embed = discord.Embed(
        title = 'Coronavirus disease (COVID-19)',
        timestamp = ctx.message.created_at,
        colour = discord.Colour.red()
    )
    Embed.set_author(name = 'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    Embed.add_field(name = 'Basic protective measures against the new coronavirus', value = '**● Wash your hands frequently.\n● Maintain social distancing.\n● Avoid touching eyes, nose and mouth.\n● If you have fever, cough and difficulty breathing, seek medical care early.\n● Stay informed and follow advice given by your healthcare provider.**', inline = False)
    Embed.add_field(name = 'Common symptoms:', value = '**● Fever.\n● Tiredness.\n● Dry cough.**', inline = False)
    Embed.add_field(name = 'Some people may experience:', value = '**● Aches and pains.\n● Nasal congestion.\n● Runny nose.\n● Sore throat.\n● Diarrhoea.**', inline = False)
    Embed.add_field(name = 'Learn more on who.int', value = '**● https://www.who.int/emergencies/diseases/novel-coronavirus-2019**', inline = False)
    Embed.add_field(name = 'Advice for public', value = '**● https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public**', inline = False)
    Embed.add_field(name = 'Q&A on coronaviruses', value = '**● https://www.who.int/news-room/q-a-detail/q-a-coronaviruses**', inline = False)
    Embed.add_field(name = 'Worldometers', value = '**● https://www.worldometers.info/coronavirus/**', inline = False)
    Embed.add_field(name = 'Johns Hopkins Coronaviruses Dashboard', value = '**● https://coronavirus.jhu.edu/map.html**', inline = False)
    Embed.add_field(name = 'NitroStudio Database (based on JHU CSSE)', value = '**● https://github.com/Nitro1231/COVID-19-Actions/tree/master/LastUpdated**', inline = False)
    Embed.add_field(name = 'CoronaLive', value = '**● https://nitro1231.github.io/CoronaLive/**', inline = False)
    Embed.set_footer(text = 'NitroStudio')
    return await ctx.send(embed=Embed)

@client.command(aliases=['cl', '코로나라이브'])
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def coronaLive(ctx):
    Embed = discord.Embed(colour = discord.Colour.red())
    Embed.set_author(name = 'CoronaLive', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    return await ctx.send(embed=Embed)

@client.command()
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def admin(ctx):
    Embed = discord.Embed(
        title = 'Admin',
        description = 'Admin command for those who own the server or using DM.',
        timestamp = ctx.message.created_at,
        colour = discord.Colour.red()
    )
    Embed.set_author(name = 'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    Embed.add_field(name = '**setprefix `prefix`**', value = 'Change the prefix. You cannot use blank for the prefix.', inline = False)
    Embed.add_field(name = '**setlanguage `language`**', value = 'Change the language setting. This function is currently unavailable, but you can change the setting now. It will be automatically applied to the server or DM after the function is available.', inline = False)
    Embed.add_field(name = '**setnotification `notification`**', value = 'Change the notification setting. This command required only `True` or `False` as a perimeter. If you did not add the tag `[covid-notification]` to your text channel, it will send the notification on first index channel.', inline = False)
    Embed.set_footer(text = 'NitroStudio')
    return await ctx.send(embed=Embed)

@client.command(aliases=['핑'])
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def ping(ctx):
    embed = discord.Embed(
        title='Ping!',
        description=f'🏓 Pong! (`{round(client.latency * 1000)}ms`)',
        timestamp = ctx.message.created_at,
        colour = discord.Colour.red()
    )
    await ctx.send(embed=embed)

@client.command(aliases=['sc','단축키','단축'])
@commands.cooldown(coolDownLimit, coolDownTime, commands.BucketType.user)
async def shortcut(ctx):
    global emoji
    cType, __ = getChatInfo(ctx)
    Embed = discord.Embed(
        title = 'Shortcut',
        description = 'No more typing, just click it.',
        timestamp = ctx.message.created_at,
        colour = discord.Colour.red()
    )
    Embed.set_author(name = 'Coronavirus (COVID-19) Pandemic', icon_url = 'https://raw.githubusercontent.com/Nitro1231/COVID-19-Bot/master/COVID-19/img/virus.png', url = 'https://nitro1231.github.io/CoronaLive/')
    Embed.add_field(name = emoji[0], value = '**help**', inline = True)
    Embed.add_field(name = emoji[1], value = '**covid**', inline = True)
    Embed.add_field(name = emoji[2], value = '**top10**', inline = True)
    Embed.add_field(name = emoji[3], value = '**prediction**', inline = True)
    Embed.add_field(name = emoji[4], value = '**coronavirus**', inline = True)
    Embed.add_field(name = emoji[5], value = '**coronalive**', inline = True)
    Embed.set_footer(text = 'NitroStudio')
    msg = await ctx.send(embed=Embed)

    for e in emoji:
        await msg.add_reaction(e)

    def check(reaction, user):
        return (user == ctx.author) and (reaction.message.id == msg.id)
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=timeLimit, check=check)
        reaction = str(reaction)
    except asyncio.TimeoutError: # this will excute when the time is out.
        if cType != 'DM':
            await msg.clear_reactions()
    else:
        if reaction == emoji[0]:
            await help(ctx)
        elif reaction == emoji[1]:
            await covid(ctx)
        elif reaction == emoji[2]:
            await top10(ctx)
        elif reaction == emoji[3]:
            await prediction(ctx)
        elif reaction == emoji[4]:
            await coronavirus(ctx)
        elif reaction == emoji[5]:
            await coronaLive(ctx)
        if cType != 'DM':
            await msg.delete()

# 포럼, 데이터 프라이버시 & 라이센스, 데이터 정보

# Admin Command
@client.command()
@commands.check(adminCheck)
async def update(ctx):
    updateData()
    global lastUpdated
    await ctx.send(f'Update Finished. ({lastUpdated})')

@client.command()
@commands.check(adminCheck)
async def exit(ctx):
    return await client.logout()

# endregion

autoUpdate()
client.run(BotToken)