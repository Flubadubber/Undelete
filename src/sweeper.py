import asyncio
from typing import Final

from asyncpraw.models import Submission

from src.reddit_facade import RedditFacade
from src.structured_log import StructuredLog
from src.submission_list import SubmissionList


class RemovedPostSweeper:
    def __init__(self, reddit_facade: RedditFacade) -> None:
        self._reddit_facade: Final[RedditFacade] = reddit_facade

    async def start(
        self,
        sweep_subreddit: str,
        minimum_rank: int,
        maximum_rank: int,
        crosspost_subreddit: str,
        interval: int,
    ) -> None:
        StructuredLog.info(
            message="Starting removed post sweeper",
            sweep_subreddit=sweep_subreddit,
            minimum_rank=minimum_rank,
            maximum_rank=maximum_rank,
            crosspost_subreddit=crosspost_subreddit,
            interval=interval,
        )
        hot_submissions: Final[SubmissionList] = SubmissionList(submissions=[])
        while True:
            asyncio.create_task(
                coro=asyncio.wait_for(
                    fut=self.sweep(
                        sweep_subreddit=sweep_subreddit,
                        minimum_rank=minimum_rank,
                        maximum_rank=maximum_rank,
                        crosspost_subreddit=crosspost_subreddit,
                        hot_submissions=hot_submissions,
                    ),
                    timeout=interval - 1,
                )
            )
            await asyncio.sleep(interval)

    async def sweep(
        self,
        sweep_subreddit: str,
        minimum_rank: int,
        maximum_rank: int,
        crosspost_subreddit: str,
        hot_submissions: SubmissionList,
    ) -> None:
        StructuredLog.info(
            message="Sweeping for removed posts",
            sweep_subreddit=sweep_subreddit,
            minimum_rank=minimum_rank,
            maximum_rank=maximum_rank,
            crosspost_subreddit=crosspost_subreddit,
        )
        new_hot_submissions: Final[
            SubmissionList
        ] = await self._reddit_facade.get_hot_submissions(
            subreddit=sweep_subreddit,
            minimum_rank=minimum_rank,
            maximum_rank=maximum_rank,
        )
        removed_submissions: Final[SubmissionList] = (
            await self._reddit_facade.reload_submissions(
                submissions=hot_submissions.diff(submission_list=new_hot_submissions)
            )
        ).get_removed()
        for submission in removed_submissions.get_submissions():
            rank: int = (
                hot_submissions.get_position(submission=submission) + minimum_rank + 1
            )
            StructuredLog.info(
                message="Found removed post",
                identifier=submission.id,
                title=submission.title,
                rank=rank,
                score=submission.score,
                comment_count=submission.num_comments,
                subreddit=str(submission.subreddit),
                permalink=self._construct_permalink(submission),
            )
            asyncio.create_task(
                coro=self._reddit_facade.write_post(
                    subreddit=crosspost_subreddit,
                    title=self._construct_title(submission=submission, rank=rank),
                    url=self._construct_permalink(submission),
                )
            )
        hot_submissions.set(submissions=new_hot_submissions.get_submissions())
        StructuredLog.info(
            message="Completed sweep for removed posts",
            removed_count=len(removed_submissions),
            sweep_subreddit=sweep_subreddit,
            minimum_rank=minimum_rank,
            maximum_rank=maximum_rank,
            crosspost_subreddit=crosspost_subreddit,
        )

    @staticmethod
    def _construct_title(submission: Submission, rank: int) -> str:
        total_length: Final[int] = (
            13
            + len(str(rank))
            + len(str(submission.score))
            + len(str(submission.num_comments))
            + len(submission.title)
            + len(str(submission.subreddit))
        )
        if total_length > 300:
            submission_title: Final[str] = (
                submission.title[: len(submission.title) - total_length + 297] + "..."
            )
        else:
            submission_title: Final[str] = submission.title
        title: str = (
            f"[#{rank}|+{submission.score}|{submission.num_comments}] "
            + f"{submission_title} [r/{submission.subreddit}]"
        )
        return title

    @staticmethod
    def _construct_permalink(submission: Submission) -> str:
        return f"https://www.reddit.com{submission.permalink}"
