import json, discord, requests, os, time, random, datetime,asyncio, sys


async def kwHelp(message):
    global bottie
    nl="\n"
    out=f"""
The available commands are:
```
{nl.join(funcs)}
```
    """
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
    quoteTime=tmp.split(":")
    if "pm" in quoteTime[1]:
        print("Converting from 12 to 24h...")
        quoteTime[0]=int(quoteTime[0])+12
        quoteTime[1]=int(quoteTime[1].replace("pm",""))
    else:
        quoteTime=[int(i) for i in quoteTime]
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

async def kwExit(message):
    if isInBotchan(message):
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
    "exit"      : kwExit

}


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
    except:
        print("Not generating optionals")
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
    print(message)
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
                await bottie.send("Quote sent!")
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