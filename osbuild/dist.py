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
import shutil
from distutils.sysconfig import parse_makefile

from osbuild import config
from osbuild import command

_dist_builders = {}


def dist_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _dist_module(module)

    return False


def dist():
    shutil.rmtree(config.get_dist_dir(), ignore_errors=True)

    modules = config.load_modules()
    for module in modules:
        if not _dist_module(module):
            return False

    return True


def _dist_module(module):
    if not module.dist:
        return True

    print(("* Creating %s distribution" % module.name))
    return _dist_builders[module.build_system](module)


def _autotools_dist_builder(module):
    source_dir = module.get_source_dir()

    os.chdir(source_dir)
    command.run(["make", "distcheck"])

    makefile = parse_makefile(os.path.join(source_dir, "Makefile"))
    tarball = "%s-%s.tar.xz" % (module.name, makefile["VERSION"])

    shutil.move(os.path.join(source_dir, tarball),
                os.path.join(config.get_dist_dir(), tarball))

    return True


_dist_builders['autotools'] = _autotools_dist_builder
