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
import json
import shutil

from osbuild import config

_BUILT_MODULES = "builtmodules"
_PULLED_MODULES = "pulledmodules"
_SYSTEM_CHECK = "syscheck"


def _compute_sourcestamp(path):
  
    import sourcestamp
    return sourcestamp.compute(path)


def built_module_touch(module):

    built_modules = _load_state(_BUILT_MODULES, {})

    source_stamp = _compute_sourcestamp(module.get_source_dir())
    built_modules[module.name] = {"source_stamp": source_stamp}

    _save_state(_BUILT_MODULES, built_modules)


def pulled_module_touch(module):
    pulled_modules = _load_state(_PULLED_MODULES, {})

    pulled_modules[module.name] = {"clean_stamp": module.clean_stamp}

    _save_state(_PULLED_MODULES, pulled_modules)


def pulled_module_should_clean(module):
    pulled_module = _get_pulled_module(module)
    if pulled_module is None:
        return False

    return pulled_module.get("clean_stamp", None) != module.clean_stamp


def built_module_is_unchanged(module):
    built_module = _get_built_module(module)
    if built_module is None:
        return False

    if "source_stamp" not in built_module:
        return False

    old_source_stamp = built_module["source_stamp"]
    new_source_stamp = _compute_sourcestamp(module.get_source_dir())

    return old_source_stamp == new_source_stamp


def clean():
    print("* Deleting state")

    names = [_BUILT_MODULES, _PULLED_MODULES]

    for name in names:
        try:
            os.unlink(_get_build_state_path(name))
        except OSError:
            pass

    if not os.listdir(config.build_state_dir):
        os.rmdir(config.build_state_dir)

    shutil.rmtree(config.home_state_dir)


def _get_built_module(module):
    built_modules = _load_state(_BUILT_MODULES, {})
    return built_modules.get(module.name, None)


def _get_pulled_module(module):
    pulled_modules = _load_state(_PULLED_MODULES, {})
    return pulled_modules.get(module.name, None)


def _get_build_state_path(name):
    return os.path.join(config.build_state_dir, "%s.json" % name)


def _load_state(name, default=None):
    state = default

    try:
        with open(_get_build_state_path(name)) as f:
            state = json.load(f)
    except IOError:
        pass

    return state


def _save_state(name, state):
    with open(_get_build_state_path(name), "w+") as f:
        json.dump(state, f, indent=4)
        f.write('\n')
