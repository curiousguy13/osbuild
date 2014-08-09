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
import logging
import subprocess
import time

import plog

from osbuild import config


def run(args, retry=0, watch_log=None):
    logging.info("Running command %s" % " ".join(args))

    tries = 0
    while tries < retry + 1:
        tries = tries + 1

        process = plog.LoggedProcess(args)
        process.execute()

        result = process.wait(watch_log=watch_log)
        if result != 0:
            if tries < retry + 1:
                print(("Retrying (attempt %d) in 1 minute" % tries))
                time.sleep(60)
            else:
                raise subprocess.CalledProcessError(result, args)
        else:
            break


def run_with_runner(cmd):
    os.environ[config.runner_variable] = cmd
    return run(config.runner_bin)
