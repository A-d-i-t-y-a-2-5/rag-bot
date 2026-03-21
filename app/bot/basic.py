import logging

import discord
from discord import app_commands
from discord.ext import commands

from app.settings import AppSettings
from app.utils.io import save_file

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


@bot.command(name="upload_pdf")
async def upload_pdf(ctx: commands.Context):
    """Upload up to 5 PDF files."""
    attachments = ctx.message.attachments

    if not attachments:
        await ctx.send("Please attach at least one PDF file.")
        return

    if len(attachments) > 5:
        await ctx.send("You can only upload up to 5 PDF files at a time.")
        return

    non_pdfs = [a.filename for a in attachments if not a.filename.lower().endswith(".pdf")]
    if non_pdfs:
        await ctx.send(f"The following files are not PDFs: {', '.join(non_pdfs)}")
        return

    for attachment in attachments:
        pdf_bytes = await attachment.read()
        await save_file(pdf_bytes, attachment.filename)
        logging.info(f"{ctx.author} uploaded {attachment.filename} ({attachment.size} bytes)")

    await ctx.send(f"Successfully uploaded {len(attachments)} PDF(s): {', '.join(a.filename for a in attachments)}")


if __name__ == "__main__":
    bot.run(config.bot.secret)
