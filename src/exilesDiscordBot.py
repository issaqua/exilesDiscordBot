# Taken from https://betterprogramming.pub/how-to-make-discord-bot-commands-in-python-2cae39cbfd55 and then blended with Amunets server code for RCON commands.
#
# We're going to use this discord bot to fire off commands from discord to Conan Exiles server RCON's
# The RCON commands (see https://conanexiles.fandom.com/wiki/Rcon) are used to control the server.
# The specific RCON commands we'll be using are:
#  - listServers - lists all the servers (from the cluster.ini file) 
#  - restartServer - restarts the server
#  - listPlayers - lists all players on the server
#  - listBans - lists all banned players
#  - ban <playername> <reason> - bans a player from the server
#  - unban <playername> - unbans a player from the server
#  - kick <playername> <reason> - kicks a player from the server


# Import configparser so we can read the amunets cluster.ini file
#  - See https://pypi.org/project/configparser/ for more details
import configparser

# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord

# Import Client from the RCON library  (pip install rcon)
#  - See https://pypi.org/project/rcon/ for more details
from rcon.source import rcon

# Import Minecraft RCON (pip install mcrcon)
from mcrcon import MCRcon

# IMPORT THE OS MODULE.
import os

# IMPORT LOAD_DOTENV FUNCTION FROM DOTENV MODULE (pip install python-dotenv)
#  - See https://pypi.org/project/python-dotenv/ for more details
from dotenv import load_dotenv

# IMPORT COMMANDS FROM THE DISCORD.EXT MODULE.  See https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
from discord.ext import commands

# LOADS THE .ENV FILE THAT RESIDES ON THE SAME LEVEL AS THE SCRIPT.
load_dotenv()

# Load key variables from the environment (loaded from the .env file).
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CLUSTER_INI_PATH = os.getenv("CLUSTER_INI_PATH")

# Parse the cluster.ini file to get the list of servers and their details.
parser = configparser.ConfigParser()

# Read the cluster.ini file.
parser.read(CLUSTER_INI_PATH)

# Get the list of sections (servers) from the cluster.ini file.
sectionList = parser.sections()


# Set up the intents for the bot before we create the bot.
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Now spin up the bot with the specified prefix and the intents as defined above.
bot = commands.Bot(command_prefix="?", intents=intents)

# on_ready() EVENT LISTENER. THIS IS CALLED WHEN THE BOT IS READY TO RECEIVE COMMANDS.
#@bot.is_ready()


# ON_MESSAGE() EVENT LISTENER. NOTICE IT IS USING @BOT.EVENT AS OPPOSED TO @BOT.COMMAND().
@bot.event
async def on_message(message):
	# CHECK IF THE MESSAGE SENT TO THE CHANNEL IS "HELLO".
	if message.content == "hello":
		# SENDS A MESSAGE TO THE CHANNEL.
		await message.channel.send("I, ExilesBot, am alive!")

	# INCLUDES THE COMMANDS FOR THE BOT. WITHOUT THIS LINE, YOU CANNOT TRIGGER YOUR COMMANDS.
	await bot.process_commands(message)


@bot.command(
	name="listServers",
	help="Uses the amunets cluster.ini file to list all the servers that this bot knows about.",
	brief="List of servers (by name) that this bot knows about."
)
async def _listServers(ctx):
	serverCount = len(sectionList)

	response = "There are " + str(serverCount) + " servers in the Amunets cluster.ini file.\n"
	
	if serverCount >= 0:
		count = 1
	
		for section in sectionList:
			response = response + "Server " + str(count) + ": [" + section + "]\n"
			count = count + 1

	await ctx.channel.send(response)

@bot.command(
	name="rebootServer",
	help="Uses RCON to reboot the specified server - serverNames provided from listServers.",
	brief="Reboot server specified."
)
async def _rebootServer(ctx, serverName):

	# Get the detals from the section (server) in the cluster.ini file.
	# REVISIT - do error checking to make sure serverName is a section and that it has the required fields.
	rconHost = eval(parser[serverName]['host'])
	rconPort = eval(parser[serverName]['port'])
	rconPasswd = eval(parser[serverName]['pass'])
	with MCRcon(host=rconHost, port=int(rconPort), password=rconPasswd, timeout=5) as mcr:
		response = mcr.command("restart")
	#response = await rcon('restart', host=rconHost, port=int(rconPort), passwd=rconPasswd)
	#response = "restart, host=" + rconHost + ", port=" + rconPort + ", passwd=rconPasswd"
	await ctx.channel.send(response)


@bot.command(
	name="listPlayers",
	help="Uses RCON to ask the specified server for the list of players.",
	brief="List of players for the given server."
)
async def _listPlayers(ctx, serverName):
	# Get the detals from the section (server) in the cluster.ini file.
	# REVISIT - do error checking to make sure serverName is a section and that it has the required fields.
	rconHost = parser[serverName]['host'].strip("\"")
	rconPort = parser[serverName]['port'].strip("\"")
	rconPasswd = parser[serverName]['pass'].strip("\"")

	with MCRcon(host=rconHost, port=int(rconPort), password=rconPasswd, timeout=5) as mcr:
		response = mcr.command("listplayers")
 
	#response = await rcon('listplayers', host=rconHost, port=int(rconPort), passwd=rconPasswd)
	await ctx.channel.send(response)






@bot.command(
	name="listBans",
	help="Uses RCON to ask the specified server for the list of banned players.",
	brief="List of banned players for the given server."
)
async def _listBannedPlayers(ctx, serverName):
	# Get the detals from the section (server) in the cluster.ini file.
	# REVISIT - do error checking to make sure serverName is a section and that it has the required fields.
	rconHost = parser[serverName]['host'].strip("\"")
	rconPort = parser[serverName]['port'].strip("\"")
	rconPasswd = parser[serverName]['pass'].strip("\"")

	with MCRcon(host=rconHost, port=int(rconPort), password=rconPasswd, timeout=5) as mcr:
		response = mcr.command("listbans")
 
	await ctx.channel.send(response)

@bot.command(
	name="banPlayer",
	help="Uses RCON to ban the specified player from the server.",
	brief="Ban the player from the given server."
)
async def _banPlayer(ctx, serverName, playerName, *reasonWords):
	await ctx.channel.send("This will use RCON to ban the player from the specified server.")

@bot.command(
	name="unbanPlayer",
	help="Uses RCON to unban the specified player from the server.",
	brief="Unban the player from the given server."
)
async def _unbanPlayer(ctx, serverName, playerName):
	await ctx.channel.send("This will use RCON to unban the player from the specified server.")

@bot.command(
	name="kickPlayer",
	help="Uses RCON to tell the specified server to kick the specified player.",
	brief="Kick the players on the specified server."
)
async def _kickPlayer(ctx, serverName, playerName, *reasonWords):
	await ctx.channel.send("This will use RCON to kick the player from the specified server.")


# COMMAND $PRINT. THIS TAKES AN IN A LIST OF ARGUMENTS FROM THE USER AND SIMPLY PRINTS THE VALUES BACK TO THE CHANNEL.
@bot.command(
	# ADDS THIS VALUE TO THE $HELP PRINT MESSAGE.
	help="Looks like you need some help.",
	# ADDS THIS VALUE TO THE $HELP MESSAGE.
	brief="Prints the list of values back to the channel."
)
async def print(ctx, *args):
	response = ""

	# LOOPS THROUGH THE LIST OF ARGUMENTS THAT THE USER INPUTS.
	for arg in args:
		response = response + " " + arg

	# SENDS A MESSAGE TO THE CHANNEL USING THE CONTEXT OBJECT.
	await ctx.channel.send(response)

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run(DISCORD_TOKEN)
