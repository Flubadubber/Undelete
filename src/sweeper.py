from time import sleep
from typing import Final, List, Set

from praw import Reddit
from praw.models import Submission

from src.structured_log import StructuredLog


class Sweeper:
    def __init__(
        self,
        reddit: Reddit,
        sweeping_subreddit: str,
        sweep_limit: int,
        crosspost_subreddit: str,
    ) -> None:
        self._reddit: Final[Reddit] = reddit
        self._sweeping_subreddit: Final[str] = sweeping_subreddit
        self._sweep_limit: Final[int] = sweep_limit
        self._crosspost_subreddit: Final[str] = crosspost_subreddit
        self._submission_ids: List[str] = self._fetch_top_submission_ids()

    def run(self, recurring: bool = False) -> None:
        StructuredLog.info(message="Sweeping for removed posts")
        removed_submissions: Final[List[Submission]] = self._get_removed_submissions()
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
            self._reddit.subreddit(display_name=self._crosspost_subreddit).submit(
                title=self._construct_title(submission=submission),
                url=self._construct_permalink(submission),
            )
        if recurring:
            sleep(60)
            self.run(recurring=recurring)

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
                submission.title[: len(submission.title) - total_length + 303] + "..."
            )
        else:
            submission_title: Final[str] = submission.title
        title: str = (
            f"[#{submission.rank}|+{submission.score}|{submission.num_comments}] "
            + f"{submission_title} [/r/{submission.subreddit}]"
        )
        if len(title) > 300:
            title = title[:297] + "..."
        return title

    @staticmethod
    def _construct_permalink(submission: Submission) -> str:
        return f"https://www.reddit.com{submission.permalink}"

    def _get_removed_submissions(self) -> List[Submission]:
        StructuredLog.debug(
            message="Sweeping subreddit for removed posts",
            subreddit=self._sweeping_subreddit,
            limit=self._sweep_limit,
        )
        new_submission_ids: Final[List[str]] = self._fetch_top_submission_ids()
        submission_ids_diff: Final[Set[str]] = set(self._submission_ids) - set(
            new_submission_ids
        )
        submissions: Final[List[Submission]] = [
            self._reddit.submission(id=submission_id)
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
            subreddit=self._sweeping_subreddit,
            count=len(removed_submissions),
        )
        self._submission_ids: List[str] = new_submission_ids
        return removed_submissions

    def _fetch_top_submission_ids(self) -> List[str]:
        StructuredLog.debug(
            message="Fetching top submissions",
            subreddit=self._sweeping_subreddit,
            limit=self._sweep_limit,
        )
        submission_ids: Final[List[str]] = [
            submission.id
            for submission in self._reddit.subreddit(
                display_name=self._sweeping_subreddit
            ).hot(limit=self._sweep_limit)
        ]
        StructuredLog.debug(
            message="Fetched top submissions",
            subreddit=self._sweeping_subreddit,
            limit=self._sweep_limit,
            count=len(submission_ids),
        )
        return submission_ids
