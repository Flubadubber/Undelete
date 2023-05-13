import logging
import sys
import tomllib
from typing import Final, Dict

from praw import Reddit

from src.logging_setup import LoggingSetup
from src.sweeper import Sweeper


SWEEPING_SUBREDDIT: Final[str] = "all"
SWEEP_LIMIT: Final[int] = 100


def main():
    LoggingSetup.setup(level=logging.INFO)
    config_path: Final[str] = sys.argv[1]
    with open(file=config_path, mode="rb") as f:
        config: Final[Dict[str, str]] = tomllib.load(f)
    reddit: Final[Reddit] = Reddit(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        username=config["username"],
        password=config["password"],
        user_agent=config["user_agent"],
    )
    sweeper: Final[Sweeper] = Sweeper(
        reddit=reddit,
        sweeping_subreddit=SWEEPING_SUBREDDIT,
        sweep_limit=SWEEP_LIMIT,
        crosspost_subreddit=config["crosspost_subreddit"],
    )
    sweeper.run(recurring=True)


if __name__ == "__main__":
    main()
