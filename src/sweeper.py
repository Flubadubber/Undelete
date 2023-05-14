import asyncio
from typing import Final, List, Set

from asyncpraw.models import Submission

from src.reddit_facade import RedditFacade
from src.structured_log import StructuredLog


class RemovedPostSweeper:
    def __init__(
        self,
        reddit_facade: RedditFacade,
    ) -> None:
        self._reddit_facade: Final[RedditFacade] = reddit_facade
        self._submission_ids = []

    async def start(
        self, sweep_subreddit: str, limit: int, crosspost_subreddit: str, interval: int
    ) -> None:
        StructuredLog.info(
            message="Starting removed post sweeper",
            sweep_subreddit=sweep_subreddit,
            limit=limit,
            crosspost_subreddit=crosspost_subreddit,
            interval=interval,
        )
        self._submission_ids: List[
            str
        ] = await self._reddit_facade.get_top_submission_ids(
            subreddit=sweep_subreddit, limit=limit
        )
        while True:
            await asyncio.sleep(interval)
            asyncio.create_task(
                asyncio.wait_for(
                    fut=self.sweep(
                        sweep_subreddit=sweep_subreddit,
                        limit=limit,
                        crosspost_subreddit=crosspost_subreddit,
                    ),
                    timeout=interval - 1,
                )
            )

    async def sweep(
        self, sweep_subreddit: str, limit: int, crosspost_subreddit: str
    ) -> None:
        StructuredLog.info(
            message="Sweeping for removed posts",
            sweep_subreddit=sweep_subreddit,
            limit=limit,
            crosspost_subreddit=crosspost_subreddit,
        )
        try:
            removed_submissions: Final[
                List[Submission]
            ] = await self._get_removed_submissions(
                subreddit=sweep_subreddit, limit=limit
            )
        except Exception as e:
            StructuredLog.error(
                message="Exception while sweeping for removed posts",
                sweep_subreddit=sweep_subreddit,
                limit=limit,
                crosspost_subreddit=crosspost_subreddit,
                exception=str(e),
            )
        else:
            for submission in removed_submissions:
                StructuredLog.info(
                    message="Found removed post",
                    identifier=submission.id,
                    title=submission.title,
                    rank=submission.rank,
                    score=submission.score,
                    comment_count=submission.num_comments,
                    subreddit=str(submission.subreddit),
                    permalink=self._construct_permalink(submission),
                )
                await self._reddit_facade.write_post(
                    subreddit=crosspost_subreddit,
                    title=self._construct_title(submission=submission),
                    url=self._construct_permalink(submission),
                )

    @staticmethod
    def _construct_title(submission: Submission) -> str:
        total_length: Final[int] = (
            13
            + len(str(submission.rank))
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
            f"[#{submission.rank}|+{submission.score}|{submission.num_comments}] "
            + f"{submission_title} [r/{submission.subreddit}]"
        )
        return title

    @staticmethod
    def _construct_permalink(submission: Submission) -> str:
        return f"https://www.reddit.com{submission.permalink}"

    async def _get_removed_submissions(
        self, subreddit: str, limit: int
    ) -> List[Submission]:
        StructuredLog.debug(
            message="Sweeping subreddit for removed posts",
            subreddit=subreddit,
            limit=limit,
        )
        new_submission_ids: Final[
            List[str]
        ] = await self._reddit_facade.get_top_submission_ids(
            subreddit=subreddit, limit=limit
        )
        submission_ids_diff: Final[Set[str]] = set(self._submission_ids) - set(
            new_submission_ids
        )
        submissions: Final[List[Submission]] = [
            await self._reddit_facade.get_submission_by_id(submission_id=submission_id)
            for submission_id in submission_ids_diff
        ]
        removed_submissions: Final[List[Submission]] = [
            submission
            for submission in submissions
            if not submission.is_robot_indexable and len(submission.url) > 0
        ]
        for submission in removed_submissions:
            submission.rank = self._submission_ids.index(submission.id) + 1
        StructuredLog.debug(
            message="Retrieved removed posts",
            subreddit=subreddit,
            count=len(removed_submissions),
        )
        self._submission_ids: List[str] = new_submission_ids
        return removed_submissions
