import asyncio
import logging
import os

from aiofiles.os import listdir, remove, makedirs
import discord
from discord.ext import commands

from app.settings import AppSettings
from app.rag.extractor import pdf_text_extractor
from app.rag.service import RAGService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

config = AppSettings()
rag_service = RAGService()

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
        dest_path = os.path.join("uploads", attachment.filename)
        await attachment.save(dest_path)
        logging.info(f"{ctx.author} uploaded {attachment.filename} ({attachment.size} bytes)")
        pdf_text_extractor(dest_path)
        txt_path = os.path.splitext(dest_path)[0] + ".txt"
        logging.info(f"Extracted text from {attachment.filename} and saved to {txt_path}")
        await rag_service.ingest_document(txt_path, config.rag.collection_name, config.rag.vector_size)

    await ctx.send(f"Successfully processed {len(attachments)} PDF(s): {', '.join(a.filename for a in attachments)}")
    
async def main():
    try:
        await makedirs("uploads", exist_ok=True)
        await bot.start(config.bot.secret)
    finally:
        files = await listdir("uploads")
        for file in files:
            await remove(os.path.join("uploads", file))
        logging.info("Cleaned up uploaded files.")
        await rag_service.delete_collection(config.rag.collection_name)
        logging.info(f"Deleted collection '{config.rag.collection_name}'.")
        logging.info("Bot is shutting down...")
        await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Unexpected error caused shutdown: {e}", exc_info=True)
