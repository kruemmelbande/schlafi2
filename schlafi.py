from glob import glob
import json, discord, requests, os, time, random, datetime,asyncio


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

def kwQuote(message):
    global quote
    quote=message.contents.split("quote")[1]
    return 0
    
def kwBackup(message):
    #send the config file to the bot channel
    global bottie
    bottie.send_file(botchan, "config.json")
    
def kwRestore(message):
    global settings
    #downloads the config file 
    url=message.attachments[0]
    file=requests.get(url.url)
    settings=file.json()
    saveConfig("config.json")


def kwReset(message):
    global optionals
    optionals=getDefaultOptionals()



#########################
#all the stuff goes here#
#########################

funcs={
    "help"  : kwHelp,
    "quote" : kwQuote,
    "reset" : kwReset
}



def getDefaultOptionals():
    optionals={}
    optionals["lastmsg"]="Error loading quote"
    optionals["lasttime"]=(0,0)
    optionals["fallbackmsg"]=["Error loading quote"]

def loadConfig(name):
    #create the default optionals
    
    try:
        global settings, token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf,optionals
        with open(name, "r") as f:
            settings=json.load(f)
        token=settings["token"]
        wakechan=settings["wakechan"]
        botchan=settings["botchan"]
        prefix=settings["prefix"]
       
        fallbackmsg=settings["fallbackmsg"]
        validconf=settings["validconf"]
        optionals=getDefaultOptionals()
        if "optionals" in settings:
            for i in settings["optionals"]:
                optionals[i]=settings["optionals"][i]
        lastmsg=optionals["lastmsg"]
        quotetime=optionals["lasttime"]
        
    except:
        validconf=0
        configCreator()

                    
def configCreator():
    global token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf,msg
    settings={}
    if input("Do you want to create a full config file?")=="y":
        token=input("Please enter your bot token: ")
        botchan=input("Please enter the channel ID of the bot channel: ")
        wakechan=input("Please enter the channel ID of the wake channel: ")
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
    global token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf, quoteTime,optionals
    settings={}
    settings["token"]=token
    settings["wakechan"]=wakechan
    settings["botchan"]=botchan
    settings["prefix"]=prefix
    settings["validconf"]=1
    #generate the optionals
    if generateOptionals:
        optionals["lastmsg"]=msg
        optionals["lasttime"]=quoteTime
        optionals["fallbackmsg"]=fallbackmsg
    settings["optionals"]=optionals
    print(settings)
    with open(name, "w") as f:
        json.dump(settings, f)
    print("saved!")
quoteTime={0,0}
#intents=discord.Intents.all()
loadConfig("config.json")
#client = discord.Bot()
intents = discord.Intents.default()
intents.message_content = True
intents.emojis_and_stickers = True
#intents.all=True
client = discord.Client(intents=intents)
@client.event
async def on_ready():
    global wakie,bottie,wakechan,botchan,prefix,lastmsg,fallbackmsg,validconf

    bottie=client.get_channel(int(botchan))
    wakie=client.get_channel(int(wakechan))
    print(f'logged in as {client.user}')
    await bottie.send(f' logged in as {client.user}')
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(message)
    if message.content.startswith(prefix):
        await funcs[message.content[len(prefix):].split(" ")[0]](message)
        

client.run(token)