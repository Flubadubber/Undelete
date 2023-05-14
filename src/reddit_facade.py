from typing import Final, List

from asyncpraw import Reddit
from asyncpraw.models import Submission

from src.structured_log import StructuredLog


class RedditFacade:
    def __init__(self, reddit: Reddit) -> None:
        self._reddit: Final[Reddit] = reddit

    async def get_top_submission_ids(self, subreddit: str, limit: int) -> List[str]:
        try:
            return [
                submission.id
                async for submission in (
                    await self._reddit.subreddit(display_name=subreddit)
                ).hot(limit=limit)
            ]
        except Exception as e:
            StructuredLog.error(
                message="Exception while getting top submission ids",
                subreddit=subreddit,
                limit=limit,
                exception=str(e),
            )
            raise e

    async def get_submission_by_id(self, submission_id: str) -> Submission:
        try:
            return await self._reddit.submission(id=submission_id)
        except Exception as e:
            StructuredLog.error(
                message="Exception while getting submission by ID",
                submission_id=submission_id,
                exception=str(e),
            )
            raise e

    async def write_post(self, subreddit: str, title: str, url: str) -> None:
        try:
            await self._reddit.subreddit(display_name=subreddit).submit(
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
