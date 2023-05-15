# Description
This is a light-weight command line script which periodically checks r/all for submissions which have been removed by
moderators or admins and permalinks any removed submissions it finds on another subreddit.

# Requirements
This was written for Python version `3.10` and depends on:
* asyncpraw
* tomli

# How To Run
Follow the prerequisites section in the
[PRAW quick start guide](https://praw.readthedocs.io/en/latest/getting_started/quick_start.html) to create a reddit
account and Reddit API application. Once done, create a TOML file in this format:
```toml
[client]
client_id = "CLIENT_ID"
client_secret = "CLIENT_SECRET"
username = "USERNAME"
password = "PASSWORD"
user_agent = "USER_AGENT"

[[crosspost_subreddits]]
subreddit = "SUBREDDIT_ONE"
minimum_rank = 0
maximum_rank = 5
interval = 60

[[crosspost_subreddits]]
subreddit = "SUBREDDIT_TWO"
minimum_rank = 5
maximum_rank = 10
interval = 180
```
The `client` table contains information required to initialize the Reddit client. The `client_id`, `client_secret`, and
`user_agent` correspond to their values from the Reddit API application. The `username` and `password` correspond to the
Reddit account you intend to post from.

The `crosspost_subreddits` list contains configuration information for which subreddits you wish to post to and how
monitoring is performed. `subreddit` is the subreddit you will to post to. `minimum_rank` and `maximum_rank` are the
bounds for post rank on r/all you will monitor for that subreddit. For example, r/undelete monitors posts in the range
0 to 100, and r/longtail monitors posts in the range 100 to 1000. Lastly, `interval` is the length of time between
successive sweeps in seconds.

Run the script using this command:
```
python main.py <path-to-toml-file>
```
Where `<path-to-toml-file>` is replaced with the full filepath pointing to you TOML file