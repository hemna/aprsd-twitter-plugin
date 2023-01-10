from oslo_config import cfg

from aprsd_twitter_plugin.conf import twitter


CONF = cfg.CONF
twitter.register_opts(CONF)
