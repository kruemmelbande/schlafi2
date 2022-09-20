# Schlafi
This project is a discord bot, which can do various functions.
Its currently in development, and might break with updates.

## Installation
To install the bot, you need to have python 3.8 or higher installed.
Then, you need to install the requirements with `pip install -r requirements.txt`.
>If you run into any issues during installation, you might need the Visual C++ Build Tools. You can get them [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).


## Configuration
The bot should run you through a setup wizard, in case it doesnt find a valid config file.  
The setup wizard will ask you for the following things:

>- The token of the bot
>   - You need to have a discord bot for this. To make a bot you need to go through the [Discord Developer Portal](https://discord.com/developers/applications)
>- The prefix for the bot
>- The channel id of the bot-only channel
>    - Only the owner of the bot should have acces to this channel, since the bot can execute arbitrary code, and be reconfigured from there.
>- The channel id of the channel, where the users should interact with it.

## Features

Due to the active development, the bot will get more commands over time.  
An actively maintained list of all the commands can be seen by typing `!help` in any channel, where the bot has access to.  
The basic commands however are:
>- `!help` - Shows a list of all commands
>- `!quote` - Sets the quote, which will be send to the user channel and the set time
>- `!setTime` - Sets the time, when the quote will be send
>- `!backup` - Saves the config file, then sends it to the bot channel
>- `!restore` - Restores the config file from the bot channel
>   - You need to attach the config file to the message, when using this command

Please note that commands are case-sensitive, and the prefix can be changed in the config file (`!` is used as an example in this readme).

# Made with love, feel free to use this however you like <3