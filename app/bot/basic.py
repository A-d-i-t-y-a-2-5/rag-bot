import logging

import discord
from discord import app_commands
from discord.ext import commands

from app.settings import AppSettings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

config = AppSettings()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    
@bot.event
async def on_command_error(ctx: commands.Context, error):
    logging.error(f"Unexpected error: {error}")
    await ctx.send(f"Error: {error}")


@bot.command(name="hello")
async def hello(ctx: commands.Context):
    """Says hello!"""
    await ctx.send(f"Took you long enough, {ctx.author.mention}")
    logging.info(f"{ctx.author} has used the hello command.")


@bot.command()
async def add(ctx: commands.Context, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


if __name__ == "__main__":
    bot.run(config.bot.secret)
