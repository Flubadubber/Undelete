import asyncio
import logging
import sys
from typing import Final, Dict

import tomli
from aiohttp import ClientSession
from asyncpraw import Reddit

from src.logging_setup import LoggingSetup
from src.reddit_facade import RedditFacade
from src.structured_log import StructuredLog
from src.sweeper import RemovedPostSweeper

SWEEP_SUBREDDIT: Final[str] = "all"
SWEEP_LIMIT: Final[int] = 100
SWEEP_INTERVAL: Final[int] = 60


async def main():
    LoggingSetup.setup(level=logging.INFO)
    config_path: Final[str] = sys.argv[1]
    with open(file=config_path, mode="rb") as f:
        config: Final[Dict[str, str]] = tomli.load(f)
    session = ClientSession(trust_env=True)
    reddit: Final[Reddit] = Reddit(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        username=config["username"],
        password=config["password"],
        user_agent=config["user_agent"],
        requestor_kwargs={"session": session},
    )
    reddit_facade: Final[RedditFacade] = RedditFacade(reddit=reddit)
    sweeper: Final[RemovedPostSweeper] = RemovedPostSweeper(
        reddit_facade=reddit_facade,
    )
    try:
        await sweeper.start(
            sweep_subreddit=SWEEP_SUBREDDIT,
            limit=SWEEP_LIMIT,
            crosspost_subreddit=config["crosspost_subreddit"],
            interval=SWEEP_INTERVAL,
        )
    except asyncio.exceptions.CancelledError:
        StructuredLog.critical(message="Main thread interrupted, performing cleanup")
    finally:
        await reddit.close()


if __name__ == "__main__":
    asyncio.run(main())
