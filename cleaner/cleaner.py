# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from cleaner.runtime.executor import Executor
from cleaner.utils.logger import LoggerMixin
from cleaner.model.condition import Condition
from cleaner.model.action import Action
from cleaner.model.rule import Rule
import time
import subprocess


def check_docker_cache(threshold):
    proc = subprocess.Popen(['/bin/bash', './scripts/reclaimable_docker_cache.sh'], stdout=subprocess.PIPE)
    out, _ = proc.communicate()
    return float(out) > threshold


class Cleaner(LoggerMixin):
    def __init__(self, cool_down_time=2):
        self.rules = {}
        self.cool_down_time = cool_down_time

    def add_rule(self, key, rule):
        if key not in self.rules:
            self.logger.info("add rule with key %s.", key)
            self.rules[key] = rule

    def add_docker_cache_rule(self):
        condition = Condition(key="docker_cache_condition",
                              input_data=1,
                              method=check_docker_cache)
        action = Action(key="docker_cache_action",
                        command="docker system prune -af")
        rule = Rule(key="docker_cache_rule",
                    condition=condition,
                    action=action)
        self.add_rule(rule.key, rule)

    def run(self):
        executor = Executor()
        executor.start()
        while True:
            for (key, rule) in self.rules.items():
                executor.run_async(key, rule)
            time.sleep(self.cool_down_time)


if __name__ == "__main__":
    cleaner = Cleaner()
    cleaner.add_docker_cache_rule()
    cleaner.run()