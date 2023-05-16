from typing import Final, AsyncGenerator

from asyncpraw import Reddit
from asyncpraw.models import Subreddit, Submission

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

    async def get_hot_submissions(
        self, subreddit: str, minimum_rank: int, maximum_rank: int
    ) -> SubmissionList:
        try:
            return SubmissionList(
                submissions=[
                    submission
                    async for submission in (
                        await self.get_subreddit(subreddit=subreddit)
                    ).hot(limit=maximum_rank)
                ]
            )[minimum_rank:]
        except Exception as e:
            StructuredLog.error(
                message="Exception while getting top submissions",
                subreddit=subreddit,
                minimum_rank=minimum_rank,
                maximum_rank=maximum_rank,
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

    async def get_submission_by_id(self, submission_id: str) -> Submission:
        try:
            return await self._reddit.submission(id=submission_id)
        except Exception as e:
            StructuredLog.error(
                message="Exception while getting submission",
                submission_id=submission_id,
                exception=str(e),
            )
            raise e

    async def reload_submissions(self, submissions: SubmissionList) -> SubmissionList:
        return SubmissionList(
            submissions=[
                await self.get_submission_by_id(submission_id=submission.id)
                for submission in submissions.get_submissions()
            ]
        )

    async def get_redditor_submission_stream(
        self, username: str
    ) -> AsyncGenerator[Submission, None]:
        try:
            return (await self._reddit.redditor(name=username)).stream.submissions(
                pause_after=-1, skip_existing=True
            )
        except Exception as e:
            StructuredLog.error(
                message="Exception while getting redditor",
                username=username,
                exception=str(e),
            )
            raise e
