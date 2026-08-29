from oslo_config import cfg

twitter_group = cfg.OptGroup(
    name="aprsd_twitter_plugin",
    title="APRSD X (Twitter) Plugin settings",
)

twitter_opts = [
    cfg.StrOpt(
        "callsign",
        help=(
            "Callsign allowed to post to X. "
            "Any callsign starting with this value will be allowed to post. "
            "For example, setting WB4BOR allows WB4BOR-1, WB4BOR-9, etc."
        ),
    ),
    cfg.StrOpt(
        "apiKey",
        help=(
            "Your X (Twitter) API Key (Consumer Key). "
            "Obtain from https://developer.x.com/en/portal/dashboard"
        ),
    ),
    cfg.StrOpt(
        "apiKey_secret",
        help="Your X (Twitter) API Key Secret (Consumer Secret).",
    ),
    cfg.StrOpt(
        "access_token",
        help=(
            "The X (Twitter) Access Token for your account. "
            "Generate under 'Keys and tokens' in the developer portal."
        ),
    ),
    cfg.StrOpt(
        "access_token_secret",
        help="The X (Twitter) Access Token Secret for your account.",
    ),
    cfg.BoolOpt(
        "add_aprs_hashtag",
        default=True,
        help="Automatically add #aprs #aprsd #hamradio hashtags to every post.",
    ),
]

ALL_OPTS = twitter_opts


def register_opts(cfg):
    cfg.register_group(twitter_group)
    cfg.register_opts(ALL_OPTS, group=twitter_group)


def list_opts():
    return {
        twitter_group.name: ALL_OPTS,
    }
