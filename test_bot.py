import betamax
import json
import praw
from base64 import b64encode
from betamax_serializers import pretty_json
from urllib.parse import quote_plus

from bot import BigBenBot


SUBREDDIT = 'BigBenBot'


def b64_string(input_string):
    """Return a base64 encoded string (not bytes) from input_string."""
    return b64encode(input_string.encode('utf-8')).decode('utf-8')


def filter_access_token(interaction, current_cassette):
    """Add Betamax placeholder to filter access token."""
    request_uri = interaction.data['request']['uri']
    response = interaction.data['response']

    # We only care about requests that generate an access token.
    if ('api/v1/access_token' not in request_uri or
            response['status']['code'] != 200):
        return
    body = response['body']['string']
    try:
        token = json.loads(body)['access_token']
    except (KeyError, TypeError, ValueError):
        return

    # If we succeeded in finding the token, add it to the placeholders for this
    # cassette.
    current_cassette.placeholders.append(
            betamax.cassette.cassette.Placeholder(
                placeholder='<ACCESS_TOKEN>', replace=token))


betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.before_record(callback=filter_access_token)


class IntegrationTest:
    def setup(self):
        self.reddit = praw.Reddit(user_agent='BigBenBot test suite')
        self.bot = BigBenBot(self.reddit, self.reddit.subreddit(SUBREDDIT))

        http = self.reddit._core._requestor._http
        http.headers['Accept-Encoding'] = 'identity'
        self.recorder = betamax.Betamax(http,
                                        cassette_library_dir='cassettes')

        # Prepare placeholders for sensitive information.
        placeholders = {
            attr: getattr(self.reddit.config, attr)
            for attr in "client_id client_secret username password".split()}

        # Password is sent URL-encoded.
        placeholders['password'] = quote_plus(placeholders['password'])

        # Client ID and secret are sent in base-64 encoding.
        placeholders['basic_auth'] = b64_string(
            "{}:{}".format(placeholders['client_id'],
                           placeholders['client_secret']))

        # Add the placeholders.
        with betamax.Betamax.configure() as config:
            for key, value in placeholders.items():
                config.define_cassette_placeholder('<{}>'.format(key.upper()),
                                                   value)


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

    def test_post_time(self):
        comment = self.reddit.comment('dhb7fxz')
        with self.recorder.use_cassette('test_post_time'):
            self.bot.post_time(comment)
