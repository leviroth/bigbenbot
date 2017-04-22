import betamax
import praw
from betamax_serializers import pretty_json

from bot import BigBenBot


SUBREDDIT = 'BigBenBot'


betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'


class IntegrationTest:
    def setup(self):
        self.reddit = praw.Reddit(user_agent='BigBenBot test suite')
        self.bot = BigBenBot(self.reddit, self.reddit.subreddit(SUBREDDIT))

        http = self.reddit._core._requestor._http
        http.headers['Accept-Encoding'] = 'identity'
        self.recorder = betamax.Betamax(http,
                                        cassette_library_dir='cassettes')


class TestBigBenBot(IntegrationTest):
    def test_check_comment__valid(self):
        comment = self.reddit.comment('dhb7fxz')
        with self.recorder.use_cassette('test_check_comment__valid'):
            assert self.bot.check_comment(comment)

    def test_check_comment__no_command(self):
        comment = self.reddit.comment('dhb7goj')
        with self.recorder.use_cassette('test_check_comment__no_command'):
            assert not self.bot.check_comment(comment)

    def test_check_comment__not_top_level(self):
        comment = self.reddit.comment('dhb7h42')
        with self.recorder.use_cassette('test_check_comment__not_top_level'):
            assert not self.bot.check_comment(comment)

    def test_check_comment__removed(self):
        comment = self.reddit.comment('dhb7g3w')
        with self.recorder.use_cassette('test_check_comment__removed'):
            assert not self.bot.check_comment(comment)
