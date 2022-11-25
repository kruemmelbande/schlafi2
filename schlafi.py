import json, discord, requests, os, time, random, datetime,asyncio, sys, importlib,subprocess


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
    await message.channel.send(out)

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
        global bottie
        if "fromautosave" in message.content.lower():
            await bottie.send("Sending last backed up config...")
            await bottie.send(file=discord.File("backup.json"))
        else:
            #send the config file to the bot channel

            saveConfig("config.json")
            await bottie.send("Sending backup...")
            await bottie.send(file=discord.File("config.json"))

async def kwRestore(message):
    global settings
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        if "fromautosave" in message.content.lower():
            try:
                loadConfig("backup.json")
                saveConfig("config.json")
            except:
                await message.channel.send("Failed to restore from autosave!")

        else:
            #DO A BACKUP! (i dont know why i didnt do this before, i wouldnt trust myself with something mission critical)
            saveConfig("backup.json")
            #^look past me, this was literally a single line of code, you could have done this before

            #downloads the config file
            try:
                url=message.attachments[0]
                file=requests.get(url.url)
                settings=file.json()
                with open("config.json","w") as f:
                    f.write(json.dumps(settings, indent=4))
                loadConfig("config.json")
                saveConfig("config.json")
                await message.channel.send("Restore successful!")
            except:
                await message.channel.send("Restore failed, undoing changes...")
                try:
                    loadConfig("backup.json")
                    saveConfig("config.json")
                except:
                    await message.channel.send("Undoing changes failed! (if you are seing this, i feel sorry for you. Ill force an undo for now, but your config file looks corrupted. You should probably fix that, by creating a new config file.)")
                    #force an undo
                    try:
                        old=open("backup.json","r")
                        new=open("config.json","w")
                        #copy the backup file to the config file
                        new.write(old.read())
                    except:
                        await message.channel.send("Cant undo changes (like.. At all)! maybe your disk is full, you dont have write permissions or i messed up my code. \n `F`")
async def kwBash(message):
    global botchan
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        command=message.content.split("bash")[1]
        global timeout
        print("Executing bash command: ", command)
        await message.channel.send("Executing bash command: "+command)
        try:
            out=subprocess.check_output(command, shell=True, timeout=timeout)
        except subprocess.CalledProcessError as e:
            await message.channel.send(f"Command returned error code {e.returncode}")
            return 1
        try:
            await message.channel.send(f"Bash command executed! \n Output:\n```{out.decode('utf-8')}```")
        except:
            await message.channel.send("Bash command executed! \n Output:\n```(too long to display)```")
            with open("bashout.txt","w") as f:
                f.write(out.decode('utf-8'))
            try:
                await message.channel.send(file=discord.File("bashout.txt"))
            except:
                print("Failed to send bash output. Either output is too long or i messed up my code.")
async def kwReset(message):
    global optionals
    saveConfig("backup.json")
    optionals=getDefaultOptionals()
    saveConfig("config.json")

async def kwAddFallback(message):
    global fallbackmsg
    if not isInBotchan(message):
        await message.channel.send("Command is not allowed in this channel!")
        return 1
    else:
        fallbackmsg.append(" ".join(message.content.strip().split(" ")[1:]))
        saveConfig("config.json")
        await message.channel.send("Added fallback message!")
        msg=""
        for i in enumerate(fallbackmsg):
            msg+=f"{i[0]}: {i[1]}\n"
        await message.channel.send(f"Current fallback messages:``` {msg}```")

async def kwListFallbacks(message):
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

async def kwWhatIs(message):
    global settings, audEnabled, audToken
    if not audEnabled:
        await message.channel.send("Aud is not enabled!")
        return 0
    humming=" !humming" in message.content.lower()
    content=message.content.replace(" !humming","").strip()
    if len(content.split(" "))>1:
        #we probably have a link there
        print("url")
        url=content.split(" ")[-1]
        await message.channel.send(audResolve(url, humming))
    else:
        #we probably have an attachment
        print("attachment")
        try:
            attachment=message.attachments[0]
            url=attachment.url
            print("\n",url, " : ", message.attachments)
            if url!=None:
                await message.channel.send(audResolve(url, humming))
                return
        except Exception as e:
            print(e)
        await message.channel.send("No attachment or link found!")
            
            
        

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
    "fbAdd"     : kwAddFallback,
    "fbRm"      : kwRemoveFallback,
    "fbLs"      : kwListFallbacks,
    "whatIs"    : kwWhatIs
}
firstLogin=1
doc={
    "help"      : "Shows this message",
    "quote"     : "Sets the quote to be displayed",
    "reset"     : "Partly resets the bot to default settings",
    "setTime"   : "Sets the time when the quote is displayed",
    "restore"   : "Restores the config file from a backup (You need to attach the backup file to the message), use the restore command with the argument \"fromautosave\" to restore from a local autosave",
    "backup"    : "Sends a backup of the config file to the bot channel, use the restore command with the argument \"fromautosave\" to send the last autosave instead",
    "bash"      : "Executes a bash command",
    "exit"      : "Exits the bot",
    "fbAdd"     : "Adds a fallback message",
    "fbRm"      : "Removes a fallback message",
    "fbLs"      : "Lists all fallback messages",
    "whatIs"    : "If enabled, you can use it with a link or attachment to get the title of the music in a video or audio file"
}

def regenerateQuote():
    global quote, fallbackmsg
    quote=random.choice(fallbackmsg)
    saveConfig("config.json")

def isInBotchan(message):
    global botchan
    re=int(botchan)==int(message.channel.id)
    if not re:
        print(f"missmatch: {botchan} vs {message.channel.id}")
    return re

def audResolve(url, humming=False):
    global audEnabled, audToken
    if not audEnabled:
        return "Aud is not enabled!"
    try:
        data = {
        'api_token': audToken,
        "url": url,
        'return': 'spotify',
        }
        if humming:
            result = requests.post('https://api.audd.io/recognizeWithOffset/', data=data)
        else:
            result = requests.post('https://api.audd.io/', data=data)
        out=result.json()
        res=""
        if not out["status"] == "success":
            if "error" in out:
                if "error_message" in out["error"]:
                    r="There was an error finding the song: ```"+out["error"]["error_message"]+"```"
                    return r
            print(out)
            return "There was an error finding the song!"
        if not humming:
            if out['status'] == 'success':
                r=out['result']
                res+=(f"Song recognized as: {r['artist']} - {r['title']} ({r['release_date']})\n")
                res+=(f"Song link: {r['song_link']} \n")
                res+=(f"Spotify: {r['spotify']['external_urls']['spotify']}") if r['spotify'] else print("Spotify: Not found")
                return res
            print(json.dumps(out, indent=4))
            return f"Song not found! (Maybe try {prefix}whatIs !humming {url})"
        else:
            if out['status'] == 'success':
                print(json.dumps(out, indent=4))
                r="The possible results are:\n"
                for i in out['result']["list"]:
                    r+=f"{i['artist']} - {i['title']} ({i['score']}% certain)\n"
                return r
    except Exception as e:
        print(e, url)
        return "Failed to find match."

def getDefaultOptionals():
    optionals={}
    optionals["lastmsg"]="Error loading quote"
    optionals["lasttime"]=(0,0)
    optionals["fallbackmsg"]=["Error loading quote"]
    optionals["bashTimeout"]=9999
    optionals["audEnabled"]=False
    optionals["audToken"]=None
    return optionals

def loadConfig(name):
    #create the default optionals

    try:
        global settings, token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf,optionals, quoteTime, quote, timeout, audEnabled, audToken
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
        timeout=optionals["bashTimeout"]
        if optionals["audEnabled"]:
            audEnabled=True
            audToken=optionals["audToken"]
        else:
            audEnabled=False
            audToken=None
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
        if input("Do you want to enable the aud.io integration?").lower().strip()=="y":
            optionals["audEnabled"]=True
            optionals["audToken"]=input("Please enter your aud.io token: ").strip()
        msg=""

        saveConfig("config.json")

    else:
        print("""
No config file found.
Please put a config file in the same directory as the bot.
 """)
def saveConfig(name,generateOptionals=1):
    print("saving...")
    global token, prefix, wakechan, botchan, lastmsg, fallbackmsg, validconf, quoteTime,optionals, quote,timeout, audEnabled, audToken
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
            optionals["bashTimeout"]=timeout
            optionals["audEnabled"]=audEnabled
            optionals["audToken"]=audToken
            print("Optionals generated!")
    except Exception as e:
        print(f"Not generating optionals, {e}")
    settings["optionals"]=optionals
    print(settings)
    with open(name, "w") as f:
        json.dump(settings, f, indent=4)
    print("saved!")
quoteTime=[0,0]

loadConfig("config.json")
intents = discord.Intents.default()
intents.message_content = True
intents.emojis_and_stickers = True
intents.auto_moderation_configuration=True
client = discord.Client(intents=intents)
@client.event
async def on_ready():
    global wakie,bottie,wakechan,botchan,prefix,lastmsg,fallbackmsg,validconf,firstLogin
    if firstLogin:
        bottie=client.get_channel(int(botchan))
        wakie=client.get_channel(int(wakechan))
        print(f' logged in as {client.user} \n To get started type `{prefix}help`')
        await bottie.send(f' logged in as `{client.user}` \n To get started type `{prefix}help`')
    else:
        await bottie.send("reconnected at "+str(datetime.datetime.now()))
        print("reconnected at "+str(datetime.datetime.now()))
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    #print(message)
    if message.content.startswith(prefix):
        if message.content[len(prefix):].split(" ")[0] in funcs:
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
            print("quote sent")
            await asyncio.sleep(61)
        else:
            await asyncio.sleep(1)
            print(now.hour,"|",now.minute,"|", now.second, "\t|", quoteTime[0],"|",quoteTime[1],"XX    ",end="\r")

quoteSendActive=1
if quoteSendActive:
    client.loop.create_task(quotesend())
client.run(token)