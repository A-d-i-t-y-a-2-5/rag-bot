import os
from typing import Any, AsyncGenerator

import aiofiles
from aiofiles.os import makedirs

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 50

async def save_file(file_bytes: bytes, file_name: str, root_dir: str = "uploads") -> str:
    await makedirs(root_dir, exist_ok=True)
    filepath = os.path.join(root_dir, file_name)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(file_bytes)
        
async def load_file(filepath: str) -> AsyncGenerator[str, Any]:
    async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
        while chunk := await f.read(DEFAULT_CHUNK_SIZE):
            yield chunk