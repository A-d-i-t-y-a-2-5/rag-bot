import time
import logging
import functools
from discord.ext import commands

logger = logging.getLogger(__name__)

def timer(func):
    @functools.wraps(func)
    async def wrapper(ctx: commands.Context, *args, **kwargs):
        start = time.perf_counter()
        try:
            return await func(ctx, *args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logger.info(f"Command '{func.__name__}' by {ctx.author} took {elapsed:.2f}s")
    return wrapper