import asyncio
from typing import Final, AsyncGenerator, Optional

from asyncpraw.models import Submission, Comment

from src.reddit_facade import RedditFacade
from src.structured_log import StructuredLog


class StickiedCommentPoller:
    def __init__(self, reddit_facade: RedditFacade) -> None:
        self._reddit_facade: Final[RedditFacade] = reddit_facade

    async def start(
        self, username: str, poller_interval: int, stream_retry_interval: int
    ) -> None:
        StructuredLog.info(
            message="Starting moderator comment poller",
            username=username,
            poller_interval=poller_interval,
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
                        message="Polling for submissions", username=username
                    )
                    if submission is None:
                        await asyncio.sleep(delay=poller_interval)
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
                await asyncio.sleep(delay=stream_retry_interval)

    async def _process_submission(self, submission: Submission) -> None:
        removed_submission: Final[Submission] = await self._get_removed_submission(
            bot_submission=submission
        )
        stickied_comment: Final[Comment] = self._get_stickied_comment(
            submission=removed_submission
        )
        if stickied_comment is not None:
            StructuredLog.info(
                message="Found stickied comment on removed post",
                submission_id=stickied_comment.link_id,
                comment_id=stickied_comment.id,
                comment_body=stickied_comment.body,
            )
            await self._reply_with_stickied_comment(
                stickied_comment=stickied_comment, submission=submission
            )

    async def _get_removed_submission(self, bot_submission: Submission) -> Submission:
        return await self._reddit_facade.get_submission_by_id(
            submission_id=Submission.id_from_url(url=bot_submission.url)
        )

    @staticmethod
    def _get_stickied_comment(submission: Submission) -> Optional[Comment]:
        top_comment: Final[Comment] = submission.comments[0]
        if top_comment.stickied:
            return top_comment
        return None

    @staticmethod
    async def _reply_with_stickied_comment(
        stickied_comment: Comment, submission: Submission
    ) -> None:
        quoted_body: Final[str] = ">" + stickied_comment.body.replace(
            "\n", "\n>"
        ).replace("---", "").replace("___", "").replace("***", "")
        comment_body: Final[str] = (
            "The [following stickied comment](https://www.reddit.com"
            + f"{stickied_comment.permalink}) was added to the removed submission:\n\n"
            + f"{quoted_body}\n\nThis might help explain why the moderators of r/"
            + f"{str(stickied_comment.subreddit)} decided to remove the submission in q"
            + "uestion.\n\n*^(It might also be completely unrelated or unhelpful.)*"
        )
        await submission.reply(body=comment_body)
