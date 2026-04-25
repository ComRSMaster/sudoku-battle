import asyncio
import logging
import sys

from backend.server import run_server
from bot.bot import run_bot


async def main() -> None:
    await asyncio.gather(run_bot(), run_server())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
