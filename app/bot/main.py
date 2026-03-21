import asyncio
import logging
import os

from aiofiles.os import listdir, remove, makedirs
import discord
from discord.ext import commands
from sentence_transformers import SentenceTransformer

from app.llm.chat import build_messages, chat
from app.rag.transform import embed
from app.rag.extractor import pdf_text_extractor
from app.rag.service import RAGService
from app.settings import AppSettings
from app.utils.timer import timer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

config = AppSettings()
rag_service = RAGService()
embedder = SentenceTransformer(config.embedder.model_name)

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


@bot.command(name="upload")
@timer
async def upload(ctx: commands.Context):
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
        await rag_service.ingest_document(txt_path, config.rag.collection_name, embedder)

    await ctx.send(f"Successfully processed {len(attachments)} PDF(s): {', '.join(a.filename for a in attachments)}")
    
@bot.command(name="ask")
@timer
async def ask(ctx: commands.Context, *, query: str = commands.param(description="The question to ask")):
    """Ask a question based on the uploaded documents."""
    if not query:
        await ctx.send("Please provide a question to ask.")
        return
    
    await ctx.send("Thinking...")
    query_embedding = embed(query, embedder)

    logging.info(f"{ctx.author} asked: {query}")
    
    results = await rag_service.search(
        collection_name=config.rag.collection_name,
        query_vector=query_embedding,
        retrieval_limit=5,
        score_threshold=0.25,
    )
    
    if not results:
        await ctx.send("No relevant documents found in the knowledge base.")
    else:
        await ctx.send(f"Found {len(results)} relevant document(s). Generating answer...")
        
    context = "\n\n".join([point.payload["original_text"] for point in results])
    messages = build_messages(query=query, context=context)
    answer = chat(messages)
    
    await ctx.send(f"**Answer:** {answer}")
    
async def main():
    try:
        await makedirs("uploads", exist_ok=True)
        await rag_service.create_collection(config.rag.collection_name, config.rag.vector_size)
        logging.info(f"Created collection '{config.rag.collection_name}' in vector database.")
        logging.info("Starting bot...")
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
        logging.error(f"Unexpected error caused shutdown: {e}")
