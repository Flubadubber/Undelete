# Description
This is a light-weight command line script which periodically checks /r/all for submissions which have been removed by
moderators or admins and permalinks any removed submissions it finds on another subreddit.

# Requirements
This was written using Python version `3.11` and only depends on one external package,
[PRAW](https://praw.readthedocs.io/en/stable/)

# How To Run
Follow the prerequisites section in the
[PRAW quick start guide](https://praw.readthedocs.io/en/latest/getting_started/quick_start.html) to create a reddit
account and Reddit API application. Once done, create a TOML file in this format:
```toml
client_id = "CLIENT_ID"
client_secret = "CLIENT_SECRET"
username = "USERNAME"
password = "PASSWORD"
user_agent = "USER_AGENT"
crosspost_subreddit = "SUBREDDIT_NAME"
```
The `client_id`, `client_secret`, and `user_agent` correspond to their values from the Reddit API application. The
`username` and `password` correspond to the Reddit account you intend to post from. Lastly, `crosspost_subreddit` is the
name of the subreddit to which you want to post permalinks to removed submissions.

Run the script using this command:
```
python main.py <path-to-toml-file>
```
Where `<path-to-toml-file>` is replaced with the full filepath pointing to you TOML file