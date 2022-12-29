from oslo_config import cfg


twitter_group = cfg.OptGroup(
    name="aprsd_twitter_plugin",
    title="APRSD Twitter Plugin settings",
)

twitter_opts = [
    cfg.StrOpt(
        "callsign",
        help="Callsign allowed to send tweets! "
             "Any callsign starting with this will be allowed to tweet to"
             "the configured twitter account.  "
             "For example, if you set this to WB4BOR then any"
             "callsign starting with WB4BOR will be allowed to tweet."
             "This way WB4BOR-1 can tweet from this instance.",
    ),
    cfg.StrOpt(
        "apiKey",
        help="Your twitter apiKey"
             "Information for creating your api keys is here:  "
             "https://developer.twitter.com/en/docs/authentication/oauth-1-0a/api-key-and-secret",
    ),
    cfg.StrOpt(
        "apiKey_secret",
        help="Your twitter accounts apikey secret.",
    ),
    cfg.StrOpt(
        "access_token",
        help="The twitter access_token for your Twitter account",
    ),
    cfg.StrOpt(
        "access_token_secret",
        help="The twitter access token secret for your Twitter account",
    ),
    cfg.BoolOpt(
        "add_aprs_hashtag",
        default=True,
        help="Automatically add #aprs hash tag to every tweet?",
    ),
]

ALL_OPTS = (
    twitter_opts
)


def register_opts(cfg):
    cfg.register_group(twitter_group)
    cfg.register_opts(ALL_OPTS, group=twitter_group)


def list_opts():
    return {
        twitter_group.name: ALL_OPTS,
    }
