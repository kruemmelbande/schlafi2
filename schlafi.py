import json, discord, requests, os, time, random, datetime,asyncio, sys


async def kwHelp(message):
    global bottie, funcs, doc
    nl="\n"
    out="The available commands are:```"
    for i in funcs:
        if i in doc:
            out+=f"{i} \t: {doc[i]}\n"
        else:
            out+=f"{i}\n"
    out+="```"
    await bottie.send(out)

async def kwQuote(message):
    global quote, bottie
    quote=message.content.split("quote")[1]
    print("Quote set to ", quote)
    await bottie.send(f"Quote set to {quote}")    	
    saveConfig("config.json")
    return 0

async def kwSetTime(message):
    global quoteTime, bottie
    tmp=message.content.lower().split("settime")[1].strip()
    tmp=tmp.replace("am","")
    tmpQuoteTime=tmp.split(":")
    if "pm" in tmpQuoteTime[1]:
        print("Converting from 12 to 24h...")
        tmpQuoteTime[0]=int(tmpQuoteTime[0])+12
        tmpQuoteTime[1]=int(tmpQuoteTime[1].replace("pm",""))
    quoteTime=[int(i) for i in tmpQuoteTime]
    saveConfig("config.json")
    await bottie.send(f"Time set to {str(quoteTime[0]).zfill(2)}:{str(quoteTime[1]).zfill(2)}")
    
async def kwBackup(message):
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        #send the config file to the bot channel
        global bottie
        saveConfig("config.json")
        await bottie.send("Sending backup...")
        await bottie.send(file=discord.File("config.json"))
    
async def kwRestore(message):
    global settings
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        #downloads the config file 
        url=message.attachments[0]
        file=requests.get(url.url)
        settings=file.json()
        saveConfig("config.json")

async def kwBash(message):
    global botchan
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        command=message.content.split("bash")[1]
        print(command)
        os.system(command)
        await message.channel.send("Bash command executed!")

async def kwReset(message):
    global optionals
    optionals=getDefaultOptionals()

async def addFallback(message):
    global fallbackmsg
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        fallbackmsg.append(message.content.strip().split(" ")[1])
        saveConfig("config.json")
        await message.channel.send("Added fallback message!")
        msg=""
        for i in enumerate(fallbackmsg):
            msg+=f"{i[0]}: {i[1]}\n"
        await message.channel.send(f"Current fallback messages:``` {msg}```")
async def listFallbacks(message):
    global fallbackmsg
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        msg=""
        for i in enumerate(fallbackmsg):
            msg+=f"{i[0]}: {i[1]}\n"
        await message.channel.send(f"Current fallback messages:``` {msg}```")
        
async def kwRemoveFallback(message):
    global fallbackmsg
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        try:
            index=int(message.content.strip().split(" ")[1])
            fallbackmsg.pop(index)
            await message.channel.send("Removed fallback message!")
            msg=""
            for i in enumerate(fallbackmsg):
                msg+=f"{i[0]}: {i[1]}\n"
            await message.channel.send(f"Current fallback messages:``` {msg}```")
        except Exception:
            await message.channel.send("Message not found!")
            
async def kwExit(message):
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        await message.channel.send("Exiting...")
        saveConfig("config.json")
        sys.exit()
    


#########################
#all the stuff goes here#
#########################

funcs={
    "help"      : kwHelp,
    "quote"     : kwQuote,
    "reset"     : kwReset,
    "setTime"   : kwSetTime,
    "restore"   : kwRestore,
    "backup"    : kwBackup,
    "bash"      : kwBash,
    "exit"      : kwExit,
    "fbAdd"     : addFallback,
    "fbRm"      : kwRemoveFallback,
    "fbLs"      : listFallbacks
}

doc={
    "help"      : "Shows this message",
    "quote"     : "Sets the quote to be displayed",
    "reset"     : "Partly resets the bot to default settings",
    "setTime"   : "Sets the time when the quote is displayed",
    "restore"   : "Restores the config file from a backup",
    "backup"    : "Sends a backup of the config file to the bot channel",
    "bash"      : "Executes a bash command",
    "exit"      : "Exits the bot",
    "fbAdd"     : "Adds a fallback message",
    "fbRm"      : "Removes a fallback message",
    "fbLs"      : "Lists all fallback messages"
}


def regenerateQuote():
    global quote, fallbackmsg
    quote=random.choice(fallbackmsg)

def isInBotchan(message):
    global botchan
    re=int(botchan)==int(message.channel.id)
    if not re:
        print(f"missmatch: {botchan} vs {message.channel.id}")
    return re

def getDefaultOptionals():
    optionals={}
    optionals["lastmsg"]="Error loading quote"
    optionals["lasttime"]=(0,0)
    optionals["fallbackmsg"]=["Error loading quote"]
    return optionals

def loadConfig(name):
    #create the default optionals
    
    try:
        global settings, token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf,optionals, quoteTime, quote
        with open(name, "r") as f:
            settings=json.load(f)
        token=settings["token"]
        wakechan=settings["wakechan"]
        botchan=settings["botchan"]
        prefix=settings["prefix"]
       
        #fallbackmsg=settings["fallbackmsg"]
        validconf=settings["validconf"]
        optionals=getDefaultOptionals()
        if "optionals" in settings:
            for i in settings["optionals"]:
                try:
                    optionals[i]=settings["optionals"][i]
                except:
                    continue
        quote=optionals["lastmsg"]
        quoteTime=optionals["lasttime"]
        fallbackmsg=optionals["fallbackmsg"]
    except Exception as e:
        print(e)
        validconf=0
        configCreator()

                    
def configCreator():
    global token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf,msg
    settings={}
    if input("Do you want to create a full config file?")=="y":
        token=input("Please enter your bot token: ").strip()
        botchan=int(input("Please enter the channel ID of the bot channel: "))
        wakechan=int(input("Please enter the channel ID of the wake channel: "))
        prefix=input("Please enter the prefix for the bot: ")
        optionals=getDefaultOptionals()
        msg=""
        
        saveConfig("config.json")
       
    else:
        print("""
No config file found.
Please put a config file in the same directory as the bot.
 """)
def saveConfig(name,generateOptionals=1):
    print("saving...")
    global token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf, quoteTime,optionals, quote
    settings={}
    settings["token"]=token
    settings["wakechan"]=wakechan
    settings["botchan"]=botchan
    settings["prefix"]=prefix
    settings["validconf"]=1
    #generate the optionals
    optionals=getDefaultOptionals()
    try:
        if generateOptionals:
            print("Trying to generate optionals...")
            optionals["lasttime"]=quoteTime
            optionals["lastmsg"]=quote
            optionals["fallbackmsg"]=fallbackmsg
            print("Optionals generated!")
    except Exception as e:
        print(f"Not generating optionals, {e}")
    settings["optionals"]=optionals
    print(settings)
    with open(name, "w") as f:
        json.dump(settings, f)
    print("saved!")
quoteTime=[0,0]
#intents=discord.Intents.all()
loadConfig("config.json")
#client = discord.Bot()
intents = discord.Intents.default()
intents.message_content = True
intents.emojis_and_stickers = True
intents.auto_moderation_configuration=True
#intents.all=True
client = discord.Client(intents=intents)
@client.event
async def on_ready():
    global wakie,bottie,wakechan,botchan,prefix,lastmsg,fallbackmsg,validconf

    bottie=client.get_channel(int(botchan))
    wakie=client.get_channel(int(wakechan))
    print(f' logged in as {client.user} \n To get started type `{prefix}help`')
    await bottie.send(f' logged in as `{client.user}` \n To get started type `{prefix}help`')
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    #print(message)
    if message.content.startswith(prefix) and message.content[len(prefix):].split(" ")[0] in funcs:
        await funcs[message.content[len(prefix):].split(" ")[0]](message)
        
async def quotesend():#this is the function which sends the quote at the right time
    await client.wait_until_ready()
    await asyncio.sleep(10)
    global quote, quoteTime,sendnow, bottie, wakie

    while not client.is_closed():
        now=datetime.datetime.now()
        if (now.hour==int(quoteTime[0]) and now.minute==int(quoteTime[1])):
            sendnow=0
            print("sending quote")
            await bottie.send("Sending quote...")
            try:
                await wakie.send(str( quote))
                await bottie.send("Quote sent, regenerating...")
                regenerateQuote()
                await bottie.send("New quote: "+str(quote))
            except Exception as e:
                await bottie.send(f"Error sending quote: {e}")
            #quote=random.choice(default_quotes)
            print("quote sent")
            await asyncio.sleep(61)
        else:
            await asyncio.sleep(1)
            print(now.hour,"|",now.minute,"|", now.second, "\t|", quoteTime[0],"|",quoteTime[1],end="\r")

quoteSendActive=1
if quoteSendActive:
    client.loop.create_task(quotesend())
client.run(token)