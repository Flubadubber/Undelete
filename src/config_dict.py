from typing import TypedDict, List


class ClientConfigDict(TypedDict):
    client_id: str
    client_secret: str
    username: str
    password: str
    user_agent: str


class CrosspostSubredditConfigDict(TypedDict):
    subreddit: str
    minimum_rank: int
    maximum_rank: int
    interval: int


class ConfigDict(TypedDict):
    client: ClientConfigDict
    crosspost_subreddits: List[CrosspostSubredditConfigDict]
