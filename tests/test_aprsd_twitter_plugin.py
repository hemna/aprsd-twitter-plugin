#!/usr/bin/env python

"""Tests for `aprsd_twitter_plugin` package."""

from unittest.mock import MagicMock, patch

import pytest
import tweepy

import aprsd_twitter_plugin
from aprsd_twitter_plugin.twitter import SendTweetPlugin


class TestVersion:
    """Tests for package version metadata."""

    def test_version_is_set(self):
        """__version__ must be a non-empty string."""
        assert isinstance(aprsd_twitter_plugin.__version__, str)
        assert len(aprsd_twitter_plugin.__version__) > 0

    def test_version_not_unknown(self):
        """Version must not be 'unknown' when installed via pip install -e ."""
        assert aprsd_twitter_plugin.__version__ != "unknown"


@pytest.fixture
def mock_conf():
    """Create a mock configuration object with all required credentials set."""
    conf = MagicMock()
    conf.aprsd_twitter_plugin.callsign = "WB4BOR"
    conf.aprsd_twitter_plugin.apiKey = "test_api_key"
    conf.aprsd_twitter_plugin.apiKey_secret = "test_api_secret"
    conf.aprsd_twitter_plugin.access_token = "test_access_token"
    conf.aprsd_twitter_plugin.access_token_secret = "test_access_secret"
    conf.aprsd_twitter_plugin.add_aprs_hashtag = True
    return conf


@pytest.fixture
def plugin_instance(mock_conf):
    """Create a plugin instance with mocked config."""
    with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
        return SendTweetPlugin()


@pytest.fixture
def mock_packet():
    """Create a mock APRS packet."""
    packet = MagicMock()
    packet.from_call = "WB4BOR"
    packet.message_text = "tw This is a test post"
    return packet


class TestSendTweetPluginMetadata:
    """Tests for plugin metadata and constants."""

    def test_command_name(self, plugin_instance):
        assert plugin_instance.command_name == "tweet"

    def test_command_regex(self, plugin_instance):
        assert plugin_instance.command_regex == r"^([t][w]\s|twitter)"

    def test_initial_enabled_false(self, mock_conf):
        """enabled must be False before setup() is called."""
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(SendTweetPlugin, "setup"):
                p = SendTweetPlugin()
                assert p.enabled is False

    def test_help_method(self, plugin_instance):
        help_text = plugin_instance.help()
        assert isinstance(help_text, list)
        assert len(help_text) == 2
        assert "X (formerly Twitter)" in help_text[0]
        assert "tw <message>" in help_text[1]


class TestSetup:
    """Tests for setup() credential validation."""

    def test_setup_all_config_present(self, mock_conf):
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            p = SendTweetPlugin()
            p.setup()
            assert p.enabled is True

    def test_setup_missing_callsign(self, mock_conf):
        mock_conf.aprsd_twitter_plugin.callsign = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            p = SendTweetPlugin()
            p.setup()
            assert p.enabled is False

    def test_setup_missing_api_key(self, mock_conf):
        mock_conf.aprsd_twitter_plugin.apiKey = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            p = SendTweetPlugin()
            p.setup()
            assert p.enabled is False

    def test_setup_missing_api_key_secret(self, mock_conf):
        mock_conf.aprsd_twitter_plugin.apiKey_secret = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            p = SendTweetPlugin()
            p.setup()
            assert p.enabled is False

    def test_setup_missing_access_token(self, mock_conf):
        mock_conf.aprsd_twitter_plugin.access_token = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            p = SendTweetPlugin()
            p.setup()
            assert p.enabled is False

    def test_setup_missing_access_token_secret(self, mock_conf):
        mock_conf.aprsd_twitter_plugin.access_token_secret = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            p = SendTweetPlugin()
            p.setup()
            assert p.enabled is False

    def test_setup_no_bearer_token_field(self, mock_conf):
        """bearer_token must NOT be a config option — it was removed."""
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            p = SendTweetPlugin()
            p.setup()
            # If bearer_token was still being accessed in setup(),
            # this would raise an AttributeError on MagicMock since we
            # intentionally don't set it.
            assert p.enabled is True


class TestCreateClient:
    """Tests for _create_client() using tweepy.Client (API v2)."""

    @patch("aprsd_twitter_plugin.twitter.tweepy.Client")
    def test_create_client_success(self, mock_client_class, plugin_instance, mock_conf):
        """Client is constructed with the 4 OAuth 1.0a credentials."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            client = plugin_instance._create_client()

        assert client is mock_client
        mock_client_class.assert_called_once_with(
            consumer_key=mock_conf.aprsd_twitter_plugin.apiKey,
            consumer_secret=mock_conf.aprsd_twitter_plugin.apiKey_secret,
            access_token=mock_conf.aprsd_twitter_plugin.access_token,
            access_token_secret=mock_conf.aprsd_twitter_plugin.access_token_secret,
        )

    @patch("aprsd_twitter_plugin.twitter.tweepy.Client")
    def test_create_client_exception_returns_none(
        self, mock_client_class, plugin_instance, mock_conf
    ):
        """Returns None when tweepy.Client raises."""
        mock_client_class.side_effect = Exception("connection error")
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            client = plugin_instance._create_client()
        assert client is None

    def test_create_client_does_not_use_oauthhandler(self, plugin_instance, mock_conf):
        """_create_client must not use the deprecated tweepy.OAuthHandler."""
        with patch("aprsd_twitter_plugin.twitter.tweepy.Client") as mock_client_class:
            with patch("aprsd_twitter_plugin.twitter.tweepy.OAuthHandler") as mock_oauth:
                mock_client_class.return_value = MagicMock()
                with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
                    plugin_instance._create_client()
                mock_oauth.assert_not_called()

    def test_create_client_does_not_use_bearer_token(self, plugin_instance, mock_conf):
        """_create_client must not pass bearer_token to tweepy.Client."""
        with patch("aprsd_twitter_plugin.twitter.tweepy.Client") as mock_client_class:
            mock_client_class.return_value = MagicMock()
            with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
                plugin_instance._create_client()
            call_kwargs = mock_client_class.call_args.kwargs
            assert "bearer_token" not in call_kwargs


class TestProcess:
    """Tests for the process() message handler."""

    def test_unauthorized_callsign_rejected(self, plugin_instance, mock_conf):
        packet = MagicMock()
        packet.from_call = "N0CALL"
        packet.message_text = "tw Hello"
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            result = plugin_instance.process(packet)
        assert result == "N0CALL not authorized to post!"

    def test_authorized_callsign_with_ssid(self, plugin_instance, mock_conf):
        """WB4BOR-1 is authorized when callsign is WB4BOR."""
        packet = MagicMock()
        packet.from_call = "WB4BOR-1"
        packet.message_text = "tw Hello"
        mock_client = MagicMock()
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                result = plugin_instance.process(packet)
        assert result == "Post sent!"

    def test_client_creation_failure_returns_error(self, plugin_instance, mock_packet, mock_conf):
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=None):
                result = plugin_instance.process(mock_packet)
        assert result == "Failed to create client"

    def test_calls_create_tweet_not_update_status(self, plugin_instance, mock_packet, mock_conf):
        """Must use create_tweet() (API v2), not the removed update_status()."""
        mock_client = MagicMock()
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                plugin_instance.process(mock_packet)
        mock_client.create_tweet.assert_called_once()
        mock_client.update_status.assert_not_called()

    def test_message_command_stripped(self, plugin_instance, mock_conf):
        """'tw ' prefix is removed before posting."""
        packet = MagicMock()
        packet.from_call = "WB4BOR"
        packet.message_text = "tw Hello world from APRS!"
        mock_client = MagicMock()
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                plugin_instance.process(packet)
        call_kwargs = mock_client.create_tweet.call_args.kwargs
        assert call_kwargs["text"].startswith("Hello world from APRS!")

    def test_hashtags_appended_when_enabled(self, plugin_instance, mock_packet, mock_conf):
        mock_conf.aprsd_twitter_plugin.add_aprs_hashtag = True
        mock_client = MagicMock()
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                plugin_instance.process(mock_packet)
        text = mock_client.create_tweet.call_args.kwargs["text"]
        assert "#aprs" in text
        assert "#aprsd" in text
        assert "#hamradio" in text

    def test_hashtags_not_appended_when_disabled(self, plugin_instance, mock_packet, mock_conf):
        mock_conf.aprsd_twitter_plugin.add_aprs_hashtag = False
        mock_client = MagicMock()
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                plugin_instance.process(mock_packet)
        text = mock_client.create_tweet.call_args.kwargs["text"]
        assert "#aprs" not in text

    def test_hashtag_url_points_to_forgejo(self, plugin_instance, mock_packet, mock_conf):
        """Hashtag URL must point to git.hemna.com, not github.com."""
        mock_conf.aprsd_twitter_plugin.add_aprs_hashtag = True
        mock_client = MagicMock()
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                plugin_instance.process(mock_packet)
        text = mock_client.create_tweet.call_args.kwargs["text"]
        assert "git.hemna.com" in text
        assert "github.com" not in text

    def test_returns_post_sent_on_success(self, plugin_instance, mock_packet, mock_conf):
        mock_client = MagicMock()
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                result = plugin_instance.process(mock_packet)
        assert result == "Post sent!"

    def test_returns_error_on_forbidden(self, plugin_instance, mock_packet, mock_conf):
        """403 Forbidden → meaningful error returned to the APRS caller."""
        mock_client = MagicMock()
        mock_client.create_tweet.side_effect = tweepy.errors.Forbidden(MagicMock())
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                result = plugin_instance.process(mock_packet)
        assert result == "Failed: no write permission"

    def test_returns_error_on_tweepy_exception(self, plugin_instance, mock_packet, mock_conf):
        """General tweepy error → error returned to the APRS caller."""
        mock_client = MagicMock()
        mock_client.create_tweet.side_effect = tweepy.errors.TweepyException("rate limit")
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                result = plugin_instance.process(mock_packet)
        assert result == "Failed to post"

    def test_twitter_command_variant(self, plugin_instance, mock_conf):
        """'twitter <msg>' command works as well as 'tw <msg>'."""
        packet = MagicMock()
        packet.from_call = "WB4BOR"
        packet.message_text = "twitter Hello from ham radio"
        mock_client = MagicMock()
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin_instance, "_create_client", return_value=mock_client):
                result = plugin_instance.process(packet)
        assert result == "Post sent!"
        text = mock_client.create_tweet.call_args.kwargs["text"]
        assert text.startswith("Hello from ham radio")
