from testing.testcases import TestCase


class commentModelTests(TestCase):

    def test_comment_model(self):
        self.clear_cache()
        user = self.create_user('test_user')
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        self.assertEqual(
            comment.__str__(),
            '{} - {} says {} at tweet {}'.format(
                comment.created_at,
                user,
                comment.content,
                tweet
            )
        )