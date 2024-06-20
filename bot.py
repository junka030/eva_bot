import os
import discord

from typing import Final
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents, Client, Message

from chat import *
from music import *

"""
Set-up
"""
# load token
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
# print(TOKEN)
GIF_KEY = os.getenv('TENOR_API')


# setup
intents = Intents.default() 
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!',intents=intents)
client = Client(intents=intents)

# bot startup
@bot.event
async def on_ready() -> None:
    print(f'{bot.user.name} is now running!')

"""
Events
"""
@client.event
async def on_member_join(member):
    lobby_id = 1253416929364807751
    channel = client.get_channel(lobby_id)

    if channel:
        await client.get_channel.send(f'Hi {member.mention}, welcome to Nerv!')

# add roles
@bot.event
async def on_raw_reaction_add(payload):
    role_msg_id = 1253424552558723142;
    role_mappings = {
            '🕹️': 'commander',
            '🎛️': 'operator',
            '🖥️': 'developer',
            '🤖': 'eva-pilot',
        }

    if payload.message_id == role_msg_id:

        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member is None:
            member = await guild.fetch_member(payload.user_id)

        emoji = payload.emoji.name

        if emoji in role_mappings:
            role_name = role_mappings[emoji]
            role = discord.utils.get(guild.roles,name=role_name)

            if role:
                # remove all other roles of member
                for role_emoji, role_name in role_mappings.items():
                    existing_role = discord.utils.get(guild.roles, name=role_name)
                    if existing_role and existing_role != role:
                        await member.remove_roles(existing_role)
                
                await member.add_roles(role)

            else:
                print(f"Role '{role_name}' not found.")
        else:
            print(f"Unsupported role emoji: {emoji}")

# remove roles
@bot.event
async def on_raw_reaction_remove(payload):
    role_msg_id = 1253424552558723142;
    role_mappings = {
            '🕹️': 'commander',
            '🎛️': 'operator',
            '🖥️': 'developer',
            '🤖': 'eva-pilot',
        }

    if payload.message_id == role_msg_id:

        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member is None:
            member = await guild.fetch_member(payload.user_id)

        emoji = payload.emoji.name

        if emoji in role_mappings:
            role_name = role_mappings[emoji]
            role = discord.utils.get(guild.roles,name=role_name)

            await member.remove_roles(role)


"""
Bot commands
"""

@bot.command()
async def hello(ctx):
    await ctx.message.add_reaction('🐣')


@bot.command()
async def clear(ctx,amount):
    if amount == 'all':
        await ctx.channel.purge()
    else:
        await ctx.channel.purge(limit=(int(amount)+1))


@bot.command(name='roles')
@commands.has_permissions(administrator=True)
async def set_roles(ctx):
    await ctx.channel.purge(limit=1)

    msg = discord.Embed(
        title = "Welcome To Nerv",
        url = "https://youtu.be/o6wtDPVkKqI?si=shQv8toQzG-W7SGR",
        description="""
            Please select your roles.\n
            🕹️ : commander
            🎛️ : operator
            🖥️ : developer
            🤖 : eva-pilot
        """,
        color= 0x992D22
    )
    msg = await ctx.send(embed=msg)

    await msg.add_reaction('🕹️')
    await msg.add_reaction('🎛️')
    await msg.add_reaction('🖥️')
    await msg.add_reaction('🤖')

# hide admin commands from help
bot.get_command('hello').hidden = True
bot.get_command('roles').hidden = True
bot.get_command('clear').hidden = True
bot.get_command('help').hidden = True

# chat command
@bot.command(name='chat', help='Rei chats with you.')
async def chatting(ctx, *, msg=''):
    try:
        response = get_response(msg)
        await ctx.send(response)
    except Exception as e:
        print(f"error: {e}")

# gif command
@bot.command(name="gif", help="Rei sends gif.")
async def gif(ctx,*,term='ayanami rei'):
    term = "evangelion " + term
    await send_gif(ctx,GIF_KEY,term)

# music commands
@bot.command(name='play', help='Rei search and play music.')
async def play(ctx,*,search):
    voice_channel = ctx.author.voice.channel if ctx.author.voice else None
    if not voice_channel:
        return await ctx.send("Please join a voice channel!")
    await add_song(ctx,search)


@bot.command(name='skip', help='Rei skips the current music.')
async def skip(ctx):
    await skip_song(ctx) 


@bot.command(name='stop',help='Rei stops playing music.')
async def stop(ctx):
    await stop_song(ctx)
    
"""
Program loop
"""
# main entry point
def main() -> None:
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("Entry plug ejected...")

if __name__ == '__main__':
    main()