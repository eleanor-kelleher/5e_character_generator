import discord
from discord.ext import commands
import logging
import yaml

from src.character_generator_fifth_ed import CharacterSheet

intents = discord.Intents.all()
intents.messages = True

logging.basicConfig(level=logging.INFO)
cg_client = discord.Client(intents=intents)

with open('conf/env.conf', 'r') as config_file:
    try:
        conf = yaml.safe_load(config_file)
    except yaml.YAMLError as exc:
        logging.info(exc)

cg_client = commands.Bot(command_prefix='!cg ',
                         description='Discord Bot for randomly generating D&D 5e character sheets.',
                         intents=intents)


@cg_client.event
async def on_ready():
    logging.info(f'Logged in as {cg_client.user.name}')
    logging.info(cg_client.user.id)
    logging.info('------')


@cg_client.command(name="info")
async def provide_help_info(ctx):
    await ctx.send("Hi, I'm CharGen! \n\n"
                   "My job is to randomly generate character sheets for D&D 5th Edition.\n"
                   "All characters created are Level 1. \n"
                   "I DO NOT choose spells (too much work for me, do it yourself).\n"
                   "I currently only support races, classes and backgrounds found in the PHB, "
                   "but that may change in the future whenever Elle decides to look at this project again :cowboy:\n\n"
                   "When you're ready, type `!cg gimme` and I'll whip something up for you!")


@cg_client.command(name="gimme")
async def generate_sheet(ctx):
    character = CharacterSheet()
    data_dict = character.create_character_data_dict(ctx.message.author.display_name)
    filename = character.write_fillable_pdf(data_dict)
    await ctx.send(f"Beep boop, I have generated a character for you! \n"
                   f"Meet **{data_dict['CharacterName']}**, the {data_dict['Race']} {data_dict['ClassLevel'].split()[0]} {data_dict['Background']}.", file=discord.File(filename))

cg_client.run(conf['bot_token'])
