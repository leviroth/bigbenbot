import praw

from bot import BigBenBot


SUBREDDIT = 'BigBenBot'


class IntegrationTest:
    def setup(self):
        self.reddit = praw.Reddit(user_agent='BigBenBot test suite')
        self.bot = BigBenBot(self.reddit, self.reddit.subreddit(SUBREDDIT))


class TestBigBenBot(IntegrationTest):
    def test_check_comment__valid(self):
        comment = self.reddit.comment('dhb7fxz')
        assert self.bot.check_comment(comment)

    def test_check_comment__no_command(self):
        comment = self.reddit.comment('dhb7goj')
        assert not self.bot.check_comment(comment)

    def test_check_comment__not_top_level(self):
        comment = self.reddit.comment('dhb7h42')
        assert not self.bot.check_comment(comment)

    def test_check_comment__removed(self):
        comment = self.reddit.comment('dhb7g3w')
        assert not self.bot.check_comment(comment)
