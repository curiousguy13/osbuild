# Copyright 2013 Daniel Narvaez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json

from osbuild import config
from osbuild import environ
from osbuild import build
from osbuild import clean
from osbuild import shell


def run_build():
    if not build.build():
        return False

    return True


def setup(config_args):
    config.setup(**config_args)
    environ.setup_variables()
    return True


def cmd_clean():
    parser = argparse.ArgumentParser()
    parser.add_argument("module", nargs="?",
                        help="name of the module to clean")
    args = parser.parse_args()

    if args.module:
        if not build.clean_one(args.module):
            return False
    else:
        if not clean.clean():
            return False

    return True


def cmd_pull():
    parser = argparse.ArgumentParser()
    parser.add_argument("module", nargs="?",
                        help="name of the module to pull")
    parser.add_argument("--sources",
                        help="json dict with the sources to pull")
    args = parser.parse_args()

    if args.module:
        if not build.pull_one(args.module):
            return False
    else:
        sources = {}
        if args.sources:
            sources = json.loads(args.sources)

        if not build.pull(sources):
            return False

    return True


def cmd_shell():
    shell.start()


def cmd_build():
    parser = argparse.ArgumentParser()
    parser.add_argument("module", nargs="?",
                        help="name of the module to build")
    args = parser.parse_args()

    if args.module:
        result = build.build_one(args.module)
    else:
        result = run_build()

    return result
