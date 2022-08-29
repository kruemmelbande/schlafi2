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
funcs={
    "help": kwHelp,
    "quote": kwQuote
}

def loadConfig(name):
    try:
        global settings, token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf
        with open(name, "r") as f:
            settings=json.load(f)
        token=settings["token"]
        wakechan=settings["wakechan"]
        botchan=settings["botchan"]
        prefix=settings["prefix"]
        lastmsg=settings["lastmsg"]
        fallbackmsg=settings["fallbackmsg"]
        validconf=settings["validconf"]
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
        lastmsg="Default quote"
        fallbackmsg=["no fall back message"]
        msg=""
        
        saveConfig("config.json")
       
    else:
        print("""
        No config file found.
        Please put a config file in the same directory as the bot.
                    """)
def saveConfig(name):
    print("saving...")
    global token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf
    settings={}
    settings["token"]=token
    settings["wakechan"]=wakechan
    settings["botchan"]=botchan
    settings["prefix"]=prefix
    settings["lastmsg"]=msg
    settings["fallbackmsg"]=fallbackmsg
    settings["validconf"]=1
    print(settings)
    with open(name, "w") as f:
        json.dump(settings, f)
    print("saved!")

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