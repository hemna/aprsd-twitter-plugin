# Copyright 2015 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
This is the single point of entry to generate the sample configuration
file for Nova. It collects all the necessary info from the other modules
in this package. It is assumed that:

* every other module in this package has a 'list_opts' function which
  return a dict where
  * the keys are strings which are the group names
  * the value of each key is a list of config options for that group
* the nova.conf package doesn't have further packages with config options
* this module is only used in the context of sample file generation
"""

import collections
import importlib
import importlib.util
import os
import pkgutil

LIST_OPTS_FUNC_NAME = "list_opts"


def _tupleize(dct):
    """Take the dict of options and convert to the 2-tuple format."""
    return [(key, val) for key, val in dct.items()]


def list_opts():
    opts = collections.defaultdict(list)
    module_names = _list_module_names()
    imported_modules = _import_modules(module_names)
    _append_config_options(imported_modules, opts)
    return _tupleize(opts)


def _list_module_names():
    module_names = []
    package_path = os.path.dirname(os.path.abspath(__file__))
    for _, modname, ispkg in pkgutil.iter_modules(path=[package_path]):
        if modname == "opts" or ispkg:
            continue
        else:
            module_names.append(modname)
    return module_names


def _import_modules(module_names):
    imported_modules = []
    for modname in module_names:
        mod = importlib.import_module("aprsd_twitter_plugin.conf." + modname)
        if not hasattr(mod, LIST_OPTS_FUNC_NAME):
            msg = (
                f"The module 'aprsd_twitter_plugin.conf.{modname}' should have a "
                f"'{LIST_OPTS_FUNC_NAME}' function which returns the config options."
            )
            raise Exception(msg)
        else:
            imported_modules.append(mod)
    return imported_modules


def _append_config_options(imported_modules, config_options):
    for mod in imported_modules:
        configs = mod.list_opts()
        for key, val in configs.items():
            config_options[key].extend(val)


def export_config(format="dict"):
    """
    Export configuration options as a simple data structure.

    This function extracts configuration information from oslo_config
    option objects and returns it in a simple dict or JSON format.
    Works independently of aprsd installation.

    Args:
        format: Output format - 'dict' (default) or 'json'

    Returns:
        dict or JSON string containing all configuration options with:
        - name: option name
        - type: option type (StrOpt, BoolOpt, IntOpt, etc.)
        - default: default value
        - help: help text
        - required: whether the option is required
        - choices: list of valid choices (if applicable)
        - secret: whether the option contains secret data (if applicable)
        - min/max: min/max values for numeric types (if applicable)

    Raises:
        ImportError: if oslo_config is not installed
    """
    # Check if oslo_config is available
    if importlib.util.find_spec("oslo_config") is None:
        raise ImportError(
            "oslo_config is required to export configuration. "
            "Install it with: pip install oslo.config",
        )

    opts = list_opts()
    result = {}

    for group_name, opt_list in opts:
        result[group_name] = []
        for opt in opt_list:
            opt_dict = {
                "name": opt.name,
                "type": type(opt).__name__,
                "default": getattr(opt, "default", None),
                "help": getattr(opt, "help", ""),
                "required": not hasattr(opt, "default") or getattr(opt, "default", None) is None,
            }

            # Add additional attributes if available
            if hasattr(opt, "choices") and opt.choices:
                opt_dict["choices"] = list(opt.choices)
            if hasattr(opt, "secret") and opt.secret:
                opt_dict["secret"] = True
            if hasattr(opt, "min") and opt.min is not None:
                opt_dict["min"] = opt.min
            if hasattr(opt, "max") and opt.max is not None:
                opt_dict["max"] = opt.max

            result[group_name].append(opt_dict)

    if format == "json":
        import json

        return json.dumps(result, indent=2)
    return result
