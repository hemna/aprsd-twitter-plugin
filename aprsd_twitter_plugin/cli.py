#!/usr/bin/env python3
"""
CLI tool for aprsd-twitter-plugin configuration export.
"""

import json
import sys


def export_config_cmd(format="json"):
    """Export plugin configuration options."""
    try:
        from aprsd_twitter_plugin.conf.opts import export_config

        result = export_config(format=format)

        if format == "json":
            print(result)
        else:
            print(json.dumps(result, indent=2))

        return 0
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nTo export config, install oslo.config:", file=sys.stderr)
        print("  pip install oslo.config", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error exporting config: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point for CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Export aprsd-twitter-plugin configuration options",
    )
    parser.add_argument(
        "--format",
        choices=["dict", "json"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()
    sys.exit(export_config_cmd(format=args.format))


if __name__ == "__main__":
    main()
