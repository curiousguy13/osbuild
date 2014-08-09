from __future__ import print_function
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

import os

from osbuild import config
from osbuild import command
from osbuild import build

_checkers = {}


def check_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            _check_module(module)

    return True


def check():
    if not build.build():
        return False

    modules = config.load_modules()
    for module in modules:
        _check_module(module)

    return True


def _check_module(module):
    if not module.has_checks:
        return True

    os.chdir(module.get_source_dir())

    print(("* Checking %s" % module.name))
    return _checkers[module.build_system](module)


def _distutils_checker(module):
    command.run_with_runner("python setup.py lint")

_checkers['distutils'] = _distutils_checker


def _grunt_checker(module):
    command.run_with_runner("grunt")

_checkers["grunt"] = _grunt_checker


def _autotools_checker(module):
    command.run_with_runner("make test")

_checkers['autotools'] = _autotools_checker
