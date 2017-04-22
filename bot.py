import datetime
import praw


SUBREDDIT = 'BigBenBot'


class BigBenBot:
    def __init__(self, reddit, subreddit):
        self.reddit = reddit
        self.subreddit = subreddit

    def check_comment(self, comment):
        """Check if comment should trigger the bot."""
        return (comment.body.split(maxsplit=1)[0] == "!time"
                and comment.is_root
                and comment.banned_by is None)

    def get_time(self):
        """Return a string representing the time."""
        return datetime.datetime.today().isoformat()

    def loop(self):
        """Read comment stream and reply with time as requested."""
        for comment in self.subreddit.stream.comments():
            if self.check_comment(comment):
                self.post_time(comment)

    def post_time(self, parent):
        """Post the current time as a reply to the parent comment."""
        body = "The current time is {}.".format(self.get_time())
        parent.reply(body)


def main():
    reddit = praw.Reddit(user_agent='BigBenBot version 1.0')
    subreddit = reddit.subreddit(SUBREDDIT)
    bot = BigBenBot(reddit, subreddit)
    bot.loop()


if __name__ == '__main__':
    main()
