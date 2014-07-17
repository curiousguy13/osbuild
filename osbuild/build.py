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

import fnmatch
import os
import multiprocessing
import shutil
import subprocess
import logging

from osbuild import command
from osbuild import config
from osbuild import state
from osbuild import utils
from osbuild import git

_builders = {}
_distributors = {}


def build_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _build_module(module)

    return False


def pull_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _pull_module(module)

    return False


def pull(sources={}):
    to_pull = config.load_modules()

    if to_pull:
        print("\n= Pulling =\n")

    for module in to_pull:
        if state.pulled_module_should_clean(module):
            source_dir = module.get_source_dir()

            if os.path.exists(source_dir):
                if not _clean_module(module):
                    print("! Could not clean module, pull failed.")
                    return False

                shutil.rmtree(source_dir, ignore_errors=True)

    for module in to_pull:
        source = sources.get(module.name, {})
        if not _pull_module(module, source):
            return False

    return True


def build():
    to_build = []
    for module in config.load_modules():
        if not state.built_module_is_unchanged(module):
            to_build.append(module)

    if not to_build:
        return True

    print("\n= Building =\n")
    print("%poop:osbuild/build.py/build1%")
    for module in to_build: 
        print("%poop:osbuild/build.py/build2%")
        if not _build_module(module):
            print("%poop:osbuild/build.py/build3%")
            return False
    print("%poop:osbuild/build.py/build4%")
    return True


def _clean_module(module):
    print(("* Cleaning %s" % module.name))

    git_module = git.get_module(module)
    if os.path.exists(module.get_source_dir()):
        return git_module.clean()
    else:
        return True


def clean_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _clean_module(module)

    return False


def clean(continue_on_error=True):
    print("* Removing install directory")
    shutil.rmtree(config.install_dir, ignore_errors=True)

    for module in config.load_modules():
        if not _clean_module(module) and not continue_on_error:
            return False

    return True


def _unlink_libtool_files():
    def func(arg, dirname, fnames):
        for fname in fnmatch.filter(fnames, "*.la"):
            os.unlink(os.path.join(dirname, fname))

    os.walk(config.lib_dir, func, None)


def _pull_module(module, source=None):
    print(("* Pulling %s" % module.name))

    git_module = git.get_module(module)

    try:
        git_module.update(source)
    except subprocess.CalledProcessError:
        return False

    logging.info("{0} HEAD: {1}".format(module.name, git_module.get_head()))

    state.pulled_module_touch(module)

    return True


def _eval_option(option):
    return eval(option, {"prefix": config.install_dir})


def _build_autotools(module):
    # Workaround for aclocal 1.11 (fixed in 1.12)
    print("%poop:osbuild/build.py/_build_autotools1%")
    aclocal_path = os.path.join(config.share_dir, "aclocal")
    print("%poop:osbuild/build.py/_build_autotools2%")
    utils.ensure_dir(aclocal_path)
    print("%poop:osbuild/build.py/_build_autotools3%")

    makefile_path = os.path.join(module.get_source_dir(), module.makefile_name)
    print("%poop:osbuild/build.py/_build_autotools4%")
    if not os.path.exists(makefile_path):
        configure = os.path.join(module.get_source_dir(), "autogen.sh")
        if not os.path.exists(configure):
            configure = os.path.join(module.get_source_dir(), "configure")

        args = [configure, "--prefix", config.install_dir]

        if not module.no_libdir:
            args.extend(["--libdir", config.lib_dir])

        args.extend(module.options)

        for option in module.options_evaluated:
            args.append(_eval_option(option))

        command.run(args)
    print("%poop:osbuild/build.py/_build_autotools5%")
    jobs = multiprocessing.cpu_count() * 2
    print("%poop:osbuild/build.py/_build_autotools6%: jobs=",jobs)
    command.run(["make", "-j", "%d" % jobs])
    print("%poop:osbuild/build.py/_build_autotools7%")
    command.run(["make", "install"])
    print("%poop:osbuild/build.py/_build_autotools8%")
    _unlink_libtool_files()

_builders["autotools"] = _build_autotools


def _build_distutils(module):
    site_packages = os.path.join(config.install_dir, "lib", "python3.3",
                                 "site-packages")
    utils.ensure_dir(site_packages)

    setup = os.path.join(module.get_source_dir(), "setup.py")
    command.run(["python3.3", setup, "install", "--prefix",
                 config.install_dir])

_builders["distutils"] = _build_distutils


def _build_grunt(module):
    command.run(["volo", "-nostamp", "-f", "add"], retry=10)
    command.run(["npm", "install"], retry=10)

_builders["grunt"] = _build_grunt


def _build_npm(module):
    command.run(["npm", "install", "-g", "--prefix", config.install_dir])

_builders["npm"] = _build_npm


def _build_module(module):
    print("%poop:osbuild/build.py/_build_module1%")
    print(("* Building %s" % module.name))
    print("%poop:osbuild/build.py/_build_module2%")
    source_dir = module.get_source_dir()
    print("%poop:osbuild/build.py/_build_module3%")
    print(source_dir)
    if not os.path.exists(source_dir):
        print("Source directory does not exist. Please pull the sources "
              "before building.")
        return False
    print("%poop:osbuild/build.py/_build_module4%")
    os.chdir(source_dir)
    print("%poop:osbuild/build.py/_build_module5%")
    try:
        if module.build_system is not None:
            _builders[module.build_system](module)
    except subprocess.CalledProcessError:
        return False
    print("%poop:osbuild/build.py/_build_module6%")
    state.built_module_touch(module)
    print("%poop:osbuild/build.py/_build_module7%")
    return True
