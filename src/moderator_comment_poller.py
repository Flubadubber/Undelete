import asyncio
from typing import Final, AsyncGenerator

from asyncpraw.models import Submission

from src.reddit_facade import RedditFacade
from src.structured_log import StructuredLog


class ModeratorCommentPoller:
    def __init__(self, reddit_facade: RedditFacade) -> None:
        self._reddit_facade: Final[RedditFacade] = reddit_facade

    async def start(self, username: str, interval: int) -> None:
        StructuredLog.info(
            message="Starting moderator comment poller",
            username=username,
            interval=interval,
        )
        while True:
            try:
                stream: AsyncGenerator[
                    Submission, None
                ] = await self._reddit_facade.get_redditor_submission_stream(
                    username=username
                )
                async for submission in stream:
                    StructuredLog.info(
                        message="Polling for submission", username=username
                    )
                    if submission is None:
                        await asyncio.sleep(delay=interval)
                    else:
                        asyncio.create_task(
                            coro=self._process_submission(submission=submission)
                        )
            except Exception as e:
                StructuredLog.error(
                    message="Exception while polling for submissions",
                    username=username,
                    exception=str(e),
                )
                await asyncio.sleep(delay=interval)

    async def _process_submission(self, submission: Submission) -> None:
        return
