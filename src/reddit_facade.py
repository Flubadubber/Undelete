from typing import Final

from asyncpraw import Reddit
from asyncpraw.models import Subreddit

from src.structured_log import StructuredLog
from src.submission_list import SubmissionList


class RedditFacade:
    def __init__(self, reddit: Reddit) -> None:
        self._reddit: Final[Reddit] = reddit

    async def get_subreddit(self, subreddit: str) -> Subreddit:
        try:
            return await self._reddit.subreddit(display_name=subreddit)
        except Exception as e:
            StructuredLog.error(
                message="Exception while getting subreddit", subreddit=subreddit
            )
            raise e

    async def get_hot_submissions(self, subreddit: str, limit: int) -> SubmissionList:
        try:
            return SubmissionList(
                submissions=[
                    submission
                    async for submission in (
                        await self.get_subreddit(subreddit=subreddit)
                    ).hot(limit=limit)
                ]
            )
        except Exception as e:
            StructuredLog.error(
                message="Exception while getting top submissions",
                subreddit=subreddit,
                limit=limit,
                exception=str(e),
            )
            raise e

    async def write_post(self, subreddit: str, title: str, url: str) -> None:
        try:
            await (await self.get_subreddit(subreddit=subreddit)).submit(
                title=title, url=url
            )
        except Exception as e:
            StructuredLog.error(
                message="Exception while writing submission",
                subreddit=subreddit,
                title=title,
                url=url,
                exception=str(e),
            )
