from __future__ import annotations

from typing import Set, List

from asyncpraw.models import Submission


class SubmissionList:
    def __init__(self, submissions: List[Submission]) -> None:
        self._submissions: List[Submission] = submissions

    def __len__(self) -> int:
        return len(self._submissions)

    def get_ids(self) -> Set[str]:
        return set(submission.id for submission in self._submissions)

    def get_submissions(self) -> List[Submission]:
        return self._submissions

    def get_rank(self, submission: Submission) -> int:
        return [submission.id for submission in self._submissions].index(submission.id)

    def set(self, submissions: List[Submission]) -> None:
        self._submissions: List[Submission] = submissions

    def diff(self, submission_list: SubmissionList) -> SubmissionList:
        return SubmissionList(
            submissions=[
                submission
                for submission in self._submissions
                if submission.id in self.get_ids() - submission_list.get_ids()
            ]
        )

    def get_removed(self) -> SubmissionList:
        return SubmissionList(
            submissions=[
                submission
                for submission in self._submissions
                if self._is_removed(submission=submission)
            ]
        )

    @staticmethod
    def _is_removed(submission: Submission) -> bool:
        return (
            submission.removed_by_category is not None
            and submission.removed_by_category != "deleted"
            and submission.removed_by_category != "author"
        )
