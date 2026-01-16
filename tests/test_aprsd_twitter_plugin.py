#!/usr/bin/env python

"""Tests for `aprsd_twitter_plugin` package."""

from unittest.mock import MagicMock, patch

import pytest

from aprsd_twitter_plugin.twitter import SendTweetPlugin


@pytest.fixture
def mock_conf():
    """Create a mock configuration object."""
    conf = MagicMock()
    conf.aprsd_twitter_plugin.callsign = "WB4BOR"
    conf.aprsd_twitter_plugin.apiKey = "test_api_key"
    conf.aprsd_twitter_plugin.apiKey_secret = "test_api_secret"
    conf.aprsd_twitter_plugin.access_token = "test_access_token"
    conf.aprsd_twitter_plugin.access_token_secret = "test_access_secret"
    conf.aprsd_twitter_plugin.bearer_token = "test_bearer_token"
    conf.aprsd_twitter_plugin.add_aprs_hashtag = True
    return conf


@pytest.fixture
def plugin(mock_conf):
    """Create a plugin instance with mocked config."""
    with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
        plugin_instance = SendTweetPlugin()
        return plugin_instance


@pytest.fixture
def mock_packet():
    """Create a mock APRS packet."""
    packet = MagicMock()
    packet.from_call = "WB4BOR"
    packet.message_text = "tw This is a test tweet"
    return packet


class TestSendTweetPlugin:
    """Test cases for SendTweetPlugin."""

    def test_plugin_initialization(self, mock_conf):
        """Test that plugin initializes correctly."""
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(SendTweetPlugin, "setup"):
                plugin = SendTweetPlugin()
                assert plugin.command_name == "tweet"
                assert plugin.command_regex == r"^([t][w]\s|twitter)"
                # enabled should be False before setup() is called
                assert plugin.enabled is False

    def test_help_method(self, plugin):
        """Test the help method returns correct help text."""
        help_text = plugin.help()
        assert isinstance(help_text, list)
        assert len(help_text) == 2
        assert "twitter: Send a Tweet!!" in help_text
        assert "twitter: Format 'tw <message>'" in help_text

    def test_setup_with_all_config(self, mock_conf):
        """Test setup method when all configuration is present."""
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            plugin = SendTweetPlugin()
            plugin.setup()
            assert plugin.enabled is True

    def test_setup_missing_callsign(self, mock_conf):
        """Test setup method when callsign is missing."""
        mock_conf.aprsd_twitter_plugin.callsign = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            plugin = SendTweetPlugin()
            plugin.setup()
            assert plugin.enabled is False

    def test_setup_missing_api_key(self, mock_conf):
        """Test setup method when apiKey is missing."""
        mock_conf.aprsd_twitter_plugin.apiKey = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            plugin = SendTweetPlugin()
            plugin.setup()
            assert plugin.enabled is False

    def test_setup_missing_api_key_secret(self, mock_conf):
        """Test setup method when apiKey_secret is missing."""
        mock_conf.aprsd_twitter_plugin.apiKey_secret = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            plugin = SendTweetPlugin()
            plugin.setup()
            assert plugin.enabled is False

    def test_setup_missing_access_token(self, mock_conf):
        """Test setup method when access_token is missing."""
        mock_conf.aprsd_twitter_plugin.access_token = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            plugin = SendTweetPlugin()
            plugin.setup()
            assert plugin.enabled is False

    def test_setup_missing_access_token_secret(self, mock_conf):
        """Test setup method when access_token_secret is missing."""
        mock_conf.aprsd_twitter_plugin.access_token_secret = None
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            plugin = SendTweetPlugin()
            plugin.setup()
            assert plugin.enabled is False

    @patch("aprsd_twitter_plugin.twitter.tweepy.API")
    @patch("aprsd_twitter_plugin.twitter.tweepy.OAuthHandler")
    def test_create_client_success(self, mock_oauth, mock_api, plugin, mock_conf):
        """Test _create_client method when authentication succeeds."""
        mock_api_instance = MagicMock()
        mock_api_instance.verify_credentials.return_value = True
        mock_api.return_value = mock_api_instance

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            client = plugin._create_client()

        assert client is not None
        mock_api_instance.verify_credentials.assert_called_once()

    @patch("aprsd_twitter_plugin.twitter.tweepy.API")
    @patch("aprsd_twitter_plugin.twitter.tweepy.OAuthHandler")
    def test_create_client_auth_failure(self, mock_oauth, mock_api, plugin, mock_conf):
        """Test _create_client method when authentication fails."""
        mock_api_instance = MagicMock()
        mock_api_instance.verify_credentials.side_effect = Exception("Auth failed")
        mock_api.return_value = mock_api_instance

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            client = plugin._create_client()

        assert client is None

    def test_process_authorized_callsign(self, plugin, mock_packet, mock_conf):
        """Test process method with authorized callsign."""
        mock_client = MagicMock()
        mock_client.update_status = MagicMock()

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin, "_create_client", return_value=mock_client):
                result = plugin.process(mock_packet)

        assert result == "Tweet sent!"
        mock_client.update_status.assert_called_once()
        # Check that the message was parsed correctly (command removed)
        call_args = mock_client.update_status.call_args[0][0]
        assert "This is a test tweet" in call_args
        # Check that the command prefix "tw " is removed (not just "tw" which appears in "test")
        assert not call_args.startswith("tw ")
        assert call_args.startswith("This is a test tweet")

    def test_process_unauthorized_callsign(self, plugin, mock_conf):
        """Test process method with unauthorized callsign."""
        packet = MagicMock()
        packet.from_call = "N0CALL"
        packet.message_text = "tw This is a test tweet"

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            result = plugin.process(packet)

        assert result == "N0CALL not authorized to tweet!"

    def test_process_callsign_with_suffix(self, plugin, mock_conf):
        """Test process method with authorized callsign with suffix (e.g., WB4BOR-1)."""
        packet = MagicMock()
        packet.from_call = "WB4BOR-1"
        packet.message_text = "tw This is a test tweet"
        mock_client = MagicMock()
        mock_client.update_status = MagicMock()

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin, "_create_client", return_value=mock_client):
                result = plugin.process(packet)

        assert result == "Tweet sent!"
        mock_client.update_status.assert_called_once()

    def test_process_client_creation_failure(self, plugin, mock_packet, mock_conf):
        """Test process method when client creation fails."""
        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin, "_create_client", return_value=None):
                result = plugin.process(mock_packet)

        assert result == "Failed to Auth"

    def test_process_message_parsing(self, plugin, mock_conf):
        """Test that message parsing correctly removes the command."""
        packet = MagicMock()
        packet.from_call = "WB4BOR"
        packet.message_text = "tw Hello world from APRS!"
        mock_client = MagicMock()
        mock_client.update_status = MagicMock()

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin, "_create_client", return_value=mock_client):
                plugin.process(packet)

        call_args = mock_client.update_status.call_args[0][0]
        assert (
            call_args
            == "Hello world from APRS! #aprs #aprsd #hamradio https://github.com/hemna/aprsd-twitter-plugin"
        )

    def test_process_with_hashtag_enabled(self, plugin, mock_packet, mock_conf):
        """Test that hashtags are added when add_aprs_hashtag is enabled."""
        mock_conf.aprsd_twitter_plugin.add_aprs_hashtag = True
        mock_client = MagicMock()
        mock_client.update_status = MagicMock()

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin, "_create_client", return_value=mock_client):
                plugin.process(mock_packet)

        call_args = mock_client.update_status.call_args[0][0]
        assert "#aprs" in call_args
        assert "#aprsd" in call_args
        assert "#hamradio" in call_args

    def test_process_with_hashtag_disabled(self, plugin, mock_packet, mock_conf):
        """Test that hashtags are not added when add_aprs_hashtag is disabled."""
        mock_conf.aprsd_twitter_plugin.add_aprs_hashtag = False
        mock_client = MagicMock()
        mock_client.update_status = MagicMock()

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin, "_create_client", return_value=mock_client):
                plugin.process(mock_packet)

        call_args = mock_client.update_status.call_args[0][0]
        assert "#aprs" not in call_args
        assert call_args == "This is a test tweet"

    def test_process_twitter_command_variant(self, plugin, mock_conf):
        """Test process method with 'twitter' command instead of 'tw'."""
        packet = MagicMock()
        packet.from_call = "WB4BOR"
        packet.message_text = "twitter This is another test"
        mock_client = MagicMock()
        mock_client.update_status = MagicMock()

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin, "_create_client", return_value=mock_client):
                result = plugin.process(packet)

        assert result == "Tweet sent!"
        call_args = mock_client.update_status.call_args[0][0]
        assert "This is another test" in call_args
        # Check that command prefix "twitter " is removed
        # (not just "twitter" which appears in URL)
        assert not call_args.startswith("twitter ")
        assert call_args.startswith("This is another test")

    def test_process_empty_message(self, plugin, mock_conf):
        """Test process method with empty message after command."""
        packet = MagicMock()
        packet.from_call = "WB4BOR"
        packet.message_text = "tw"
        mock_client = MagicMock()
        mock_client.update_status = MagicMock()

        with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
            with patch.object(plugin, "_create_client", return_value=mock_client):
                plugin.process(packet)

        call_args = mock_client.update_status.call_args[0][0]
        # Should be empty or just hashtags
        assert call_args == " #aprs #aprsd #hamradio https://github.com/hemna/aprsd-twitter-plugin"

    def test_create_client_oauth_handler_initialization(self, plugin, mock_conf):
        """Test that OAuthHandler is initialized with correct credentials."""
        mock_oauth_instance = MagicMock()
        mock_oauth_class = MagicMock(return_value=mock_oauth_instance)

        with patch("aprsd_twitter_plugin.twitter.tweepy.OAuthHandler", mock_oauth_class):
            with patch("aprsd_twitter_plugin.twitter.tweepy.API") as mock_api:
                mock_api_instance = MagicMock()
                mock_api_instance.verify_credentials.return_value = True
                mock_api.return_value = mock_api_instance

                with patch("aprsd_twitter_plugin.twitter.CONF", mock_conf):
                    plugin._create_client()

        mock_oauth_class.assert_called_once_with(
            mock_conf.aprsd_twitter_plugin.apiKey,
            mock_conf.aprsd_twitter_plugin.apiKey_secret,
        )
        mock_oauth_instance.set_access_token.assert_called_once_with(
            mock_conf.aprsd_twitter_plugin.access_token,
            mock_conf.aprsd_twitter_plugin.access_token_secret,
        )
