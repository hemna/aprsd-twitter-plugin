import logging

from aprsd import messaging, plugin, trace


LOG = logging.getLogger("APRSD")


class SendTweetPlugin(plugin.APRSDRegexCommandPluginBase):

    version = "1.0"
    # Look for any command that starts with w or W
    command_regex = "^[wW]"
    # the command is for ?
    command_name = "weather"

    enabled = False

    def setup(self):
        # Do some checks here?
        self.enabled = True

    def create_threads(self):
        """This allows you to create and return a custom APRSDThread object.

        Create a child of the aprsd.threads.APRSDThread object and return it
        It will automatically get started.

        You can see an example of one here:
        https://github.com/craigerl/aprsd/blob/master/aprsd/threads.py#L141
        """
        if self.enabled:
            # You can create a background APRSDThread object here
            # Just return it for example:
            # https://github.com/hemna/aprsd-weewx-plugin/blob/master/aprsd_weewx_plugin/aprsd_weewx_plugin.py#L42-L50
            #
            return []

    @trace.trace
    def process(self, packet):

        """This is called when a received packet matches self.command_regex."""

        LOG.info("SendTweetPlugin Plugin")

        packet.get("from")
        packet.get("message_text", None)

        if self.enabled:
            # Now we can process
            return "some reply message"
        else:
            LOG.warning("SendTweetPlugin is disabled.")
            return messaging.NULL
