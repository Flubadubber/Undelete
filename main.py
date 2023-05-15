import asyncio
import logging
import sys
from typing import Final

import tomli
from aiohttp import ClientSession
from asyncpraw import Reddit

from src.config_dict import ConfigDict
from src.logging_setup import LoggingSetup
from src.reddit_facade import RedditFacade
from src.structured_log import StructuredLog
from src.sweeper import RemovedPostSweeper

SWEEP_SUBREDDIT: Final[str] = "all"


async def main():
    LoggingSetup.setup(level=logging.INFO)
    config_path: Final[str] = sys.argv[1]
    with open(file=config_path, mode="rb") as f:
        config: Final[ConfigDict] = tomli.load(f)
    session = ClientSession(trust_env=True)
    reddit: Final[Reddit] = Reddit(
        client_id=config["client"]["client_id"],
        client_secret=config["client"]["client_secret"],
        username=config["client"]["username"],
        password=config["client"]["password"],
        user_agent=config["client"]["user_agent"],
        requestor_kwargs={"session": session},
    )
    reddit_facade: Final[RedditFacade] = RedditFacade(reddit=reddit)
    sweeper: Final[RemovedPostSweeper] = RemovedPostSweeper(
        reddit_facade=reddit_facade,
    )
    try:
        await asyncio.gather(
            *[
                sweeper.start(
                    sweep_subreddit=SWEEP_SUBREDDIT,
                    minimum_rank=crosspost_subreddit_config["minimum_rank"],
                    maximum_rank=crosspost_subreddit_config["maximum_rank"],
                    crosspost_subreddit=crosspost_subreddit_config["subreddit"],
                    interval=crosspost_subreddit_config["interval"],
                )
                for crosspost_subreddit_config in config["crosspost_subreddits"]
            ],
            return_exceptions=True,
        )
    except asyncio.exceptions.CancelledError:
        StructuredLog.critical(message="Main thread interrupted, performing cleanup")
    except Exception as e:
        StructuredLog.critical(
            message="Exception while running sweepers", exception=str(e)
        )
    finally:
        await reddit.close()


if __name__ == "__main__":
    asyncio.run(main())
