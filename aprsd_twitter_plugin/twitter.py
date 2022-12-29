import logging

import tweepy
from aprsd import conf  # noqa
from aprsd import plugin
from oslo_config import cfg

import aprsd_twitter_plugin
from aprsd_twitter_plugin import conf  # noqa


CONF = cfg.CONF
LOG = logging.getLogger("APRSD")


class SendTweetPlugin(plugin.APRSDRegexCommandPluginBase):

    version = aprsd_twitter_plugin.__version__
    # Look for any command that starts with tw or tW or TW or Tw
    # or case insensitive version of 'twitter'
    command_regex = r"^([t][w]\s|twitter)"
    # the command is for ?
    command_name = "tweet"

    enabled = False

    def help(self):
        _help = [
            "twitter: Send a Tweet!!",
            "twitter: Format 'tw <message>'",
        ]
        return _help

    def setup(self):
        # Do some checks here?
        self.enabled = True

        if not CONF.aprsd_twitter_plugin.callsign:
            LOG.error(
                "No aprsd_twitter_pligin.callsign is set."
                " Callsign is needed to allow tweets!",
            )
            self.enabled = False

        # Ensure the access token exists.
        if not CONF.aprsd_twitter_plugin.apiKey:
            LOG.error(
                "No aprsd_twitter_plugin.apiKey is set!."
                " Plugin Disabled.",
            )
            self.enabled = False

        if not CONF.aprsd_twitter_plugin.apiKey_secret:
            LOG.error(
                "No aprsd_twitter_plugin.apiKey_secret is set."
                " Plugin Disabled.",
            )
            self.enabled = False

        if not CONF.aprsd_twitter_plugin.access_token:
            LOG.error(
                "No aprsd_twitter_plugin.access_token exists."
                " Plugin Disabled.",
            )
            self.enabled = False

        if not CONF.aprsd_twitter_plugin.access_token_secret:
            LOG.error(
                "No aprsd_twitter_plugin.access_token_secret exists."
                " Plugin Disabled.",
            )
            self.enabled = False

    def _create_client(self):
        """Create the twitter client object."""
        auth = tweepy.OAuthHandler(
            CONF.aprsd_twitter_plugin.apiKey,
            CONF.aprsd_twitter_plugin.apiKey_secret,
        )

        auth.set_access_token(
            CONF.aprsd_twitter_plugin.access_token,
            CONF.aprsd_twitter_plugin.access_token_secret,
        )

        api = tweepy.API(
            auth,
            wait_on_rate_limit=True,
        )

        try:
            api.verify_credentials()
            LOG.debug("Logged in to Twitter Authentication OK")
        except Exception as ex:
            LOG.error("Failed to auth to Twitter")
            LOG.exception(ex)
            return None

        return api

    def process(self, packet):

        """This is called when a received packet matches self.command_regex."""

        LOG.info("SendTweetPlugin Plugin")

        from_callsign = packet.from_call
        message = packet.message_text
        message = message.split(" ")
        del message[0]
        message = " ".join(message)

        # Now we can process
        auth_call = CONF.aprsd_twitter_plugin.callsign

        # Only allow the owner of aprsd to send a tweet
        if not from_callsign.startswith(auth_call):
            return f"{from_callsign} not authorized to tweet!"

        client = self._create_client()
        if not client:
            LOG.error("No twitter client!!")
            return "Failed to Auth"

        if CONF.aprsd_twitter_plugin.add_aprs_hashtag:
            message += (
                " #aprs #aprsd #hamradio "
                "https://github.com/hemna/aprsd-twitter-plugin"
            )

        # Now lets tweet!
        client.update_status(message)

        return "Tweet sent!"
