from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("aprsd_twitter_plugin")
except PackageNotFoundError:
    __version__ = "unknown"
