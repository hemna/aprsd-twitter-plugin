import logging

import tweepy
from aprsd import (
    conf,  # noqa
    plugin,
)
from oslo_config import cfg

import aprsd_twitter_plugin
from aprsd_twitter_plugin import conf as twitter_conf  # noqa

CONF = cfg.CONF
LOG = logging.getLogger("APRSD")


class SendTweetPlugin(plugin.APRSDRegexCommandPluginBase):
    version = aprsd_twitter_plugin.__version__
    # Look for any command that starts with tw or tW or TW or Tw
    # or case insensitive version of 'twitter'
    command_regex = r"^([t][w]\s|twitter)"
    command_name = "tweet"

    enabled = False

    def help(self):
        _help = [
            "twitter: Post to X (formerly Twitter)!",
            "twitter: Format 'tw <message>'",
        ]
        return _help

    def setup(self):
        self.enabled = True

        if not CONF.aprsd_twitter_plugin.callsign:
            LOG.error(
                "No aprsd_twitter_plugin.callsign is set. Callsign is needed to allow posting!",
            )
            self.enabled = False

        if not CONF.aprsd_twitter_plugin.apiKey:
            LOG.error(
                "No aprsd_twitter_plugin.apiKey is set. Plugin Disabled.",
            )
            self.enabled = False

        if not CONF.aprsd_twitter_plugin.apiKey_secret:
            LOG.error(
                "No aprsd_twitter_plugin.apiKey_secret is set. Plugin Disabled.",
            )
            self.enabled = False

        if not CONF.aprsd_twitter_plugin.access_token:
            LOG.error(
                "No aprsd_twitter_plugin.access_token is set. Plugin Disabled.",
            )
            self.enabled = False

        if not CONF.aprsd_twitter_plugin.access_token_secret:
            LOG.error(
                "No aprsd_twitter_plugin.access_token_secret is set. Plugin Disabled.",
            )
            self.enabled = False

    def _create_client(self):
        """Create the X/Twitter API v2 client using OAuth 1.0a."""
        try:
            client = tweepy.Client(
                consumer_key=CONF.aprsd_twitter_plugin.apiKey,
                consumer_secret=CONF.aprsd_twitter_plugin.apiKey_secret,
                access_token=CONF.aprsd_twitter_plugin.access_token,
                access_token_secret=CONF.aprsd_twitter_plugin.access_token_secret,
            )
            LOG.debug("X/Twitter client created OK")
            return client
        except Exception as ex:
            LOG.error("Failed to create X/Twitter client")
            LOG.exception(ex)
            return None

    def process(self, packet):
        """This is called when a received packet matches self.command_regex."""

        LOG.info("SendTweetPlugin Plugin")

        from_callsign = packet.from_call
        message = packet.message_text
        message = message.split(" ")
        del message[0]
        message = " ".join(message)

        # Only allow the configured callsign to post
        auth_call = CONF.aprsd_twitter_plugin.callsign
        if not from_callsign.startswith(auth_call):
            return f"{from_callsign} not authorized to post!"

        client = self._create_client()
        if not client:
            LOG.error("No X/Twitter client!")
            return "Failed to create client"

        if CONF.aprsd_twitter_plugin.add_aprs_hashtag:
            message += " #aprs #aprsd #hamradio http://git.hemna.com/hemna/aprsd-twitter-plugin"

        try:
            client.create_tweet(text=message)
        except tweepy.errors.Forbidden as ex:
            LOG.error("Forbidden — check your X developer account has write permissions")
            LOG.exception(ex)
            return "Failed: no write permission"
        except tweepy.errors.TweepyException as ex:
            LOG.error("Failed to post to X")
            LOG.exception(ex)
            return "Failed to post"

        return "Post sent!"
