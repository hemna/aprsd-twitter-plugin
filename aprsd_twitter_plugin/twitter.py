import logging

import tweepy
from aprsd import messaging, plugin, trace


LOG = logging.getLogger("APRSD")


class SendTweetPlugin(plugin.APRSDRegexCommandPluginBase):

    version = "1.0"
    # Look for any command that starts with tw or tW or TW or Tw
    command_regex = "^[tT][wW]"
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

        # Ensure the access token exists.
        if not self.config.exists("services.twitter.apiKey"):
            LOG.error("No services.twitter.apiKey exists. Plugin Disabled.")
            self.enabled = False

        if not self.config.exists("services.twitter.apiKey_secret"):
            LOG.error("No services.twitter.apiKey_secret exists. Plugin Disabled.")
            self.enabled = False

        if not self.config.exists("services.twitter.access_token"):
            LOG.error("No services.twitter.access_token exists. Plugin Disabled.")
            self.enabled = False

        if not self.config.exists("services.twitter.access_token_secret"):
            LOG.error("No services.twitter.access_token_secret exists. Plugin Disabled.")
            self.enabled = False

    def _create_client(self):
        """Create the twitter client object."""
        auth = tweepy.OAuthHandler(
            self.config.get("services.twitter.apiKey"),
            self.config.get("services.twitter.apiKey_secret"),
        )

        auth.set_access_token(
            self.config.get("services.twitter.access_token"),
            self.config.get("services.twitter.access_token_secret"),
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

    @trace.trace
    def process(self, packet):

        """This is called when a received packet matches self.command_regex."""

        LOG.info("SendTweetPlugin Plugin")

        from_callsign = packet.get("from")
        message = packet.get("message_text", None)
        message = message.split(" ")
        del message[0]
        message = " ".join(message)

        if self.enabled:
            # Now we can process
            mycall = self.config["ham"]["callsign"]

            # Only allow the owner of aprsd to send a tweet
            if not from_callsign.startswith(mycall):
                return "Unauthorized"

            client = self._create_client()
            if not client:
                LOG.error("No twitter client!!")
                return "Failed to Auth"

            # Now lets tweet!
            client.update_status(message)

            return "Tweet sent!"
        else:
            LOG.warning("SendTweetPlugin is disabled.")
            return messaging.NULL_MESSAGE
